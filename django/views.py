@login_required
@transaction.commit_on_success
def create_w(request, id):
    if Register.objects.filter(id=id).exists() and Register.objects.get(id=id).sender == request.sender:
        return create_response([id], user_friendly=True)
    else:
        return HttpResponseRedirect("/")


def map_reduce_task(request, ids):
    registers = get_registers(request)
    ids = get_ids(ids)
    if not registers:
        return HttpResponseRedirect("/")
    else:
        for register in registers:
            if ids:  # Using optimized queries:
                objects = register.objects.filter(id__in=ids).values_list("id", flat=True)
            else:
                objects = register.objects.all().values_list("id", flat=True)

            t = 0
            task_map = []

            def chunks(objects, length):  # Defining method with a generator in a loop.
                for i in xrange(0, len(objects), length):
                    yield objects[i:i+length]

            for chunk in chunks(objects, 20):
                countdown = 5*t
                t += 1
                tasks_map.append(request_by_mapper(register, chunk, countdown, datetime.now()))
        g = group(*tasks_map)
        reduce_task = chain(g, create_request_by_reduce_async.s(tasks_map))()


@login_required
def create_payment(request):
    # currency=BTC&version=1&cmd=get_callback_address&key=your_api_public_key&format=json
    public_key = os.environ.get('PUBLIC_KEY')
    private_key = os.environ.get('PRIVATE_KEY')
    # get payment info
    if request.method == "POST":
        policy_id = request.POST.get('policy_id', '')
        currency = request.POST.get('currency')
        logger.debug(currency)
        policy = InsurancePolicy.objects.get(id=policy_id)
        try:
            payment = policy.payment_id
            # if payment is NULL then exeption
            payment.id
        except Exception as e:
            # everything is ok, new user
            # create payment with coinpayment
            post_params = {
                'amount': policy.fee,
                'currency1': 'BTC',
                'currency2': currency,
                'buyer_email':
                    request.user.email,  # TODO set request.user.mail,
                'item_name': 'Policy for ' + policy.exchange.name,
                'item_number': policy.id
            }
            try:
                client = CryptoPayments(public_key, private_key)
                transaction = client.createTransaction(post_params)
                logger.debug(transaction)  # FOR DEBUG
                if len(transaction) == 0:
                    raise Exception
            except Exception as e:
                logger.error(e)
                message = 'Payment gateway is down'
                responseData = {'error': True, 'message': message}
                return JsonResponse(responseData)

            try:
                try:
                    payment = UserPayments(
                        status=0,
                        update_date=datetime.datetime.now(),
                        amount=transaction.amount,
                        address=transaction.address,
                        payment=transaction.txn_id,
                        confirms_needed=transaction.confirms_needed,
                        timeout=transaction.timeout,
                        status_url=transaction.status_url,
                        qrcode_url=transaction.qrcode_url,
                        currency=currency)

                    try:
                        default_email = os.environ.get('DJANGO_EMAIL_DEFAULT_EMAIL')
                        subject = "Cryptoins: You’re one step away from being secured"
                        message = render_to_string('first_email.html', {'user': policy.user, 'payment': payment})
                        send_mail(subject, message, default_email, [policy.user.email])
                    except Exception as e:
                        logger.error('Error on sending first email: ', e)

                except Exception as e:
                    logger.error(e)
                    responseData = {
                        'error': True,
                        'message': 'Payment Gateway Error'
                    }
                    return JsonResponse(responseData)
                else:
                    payment.save()
                    policy.payment_id = payment
                    policy.save()

            except Exception as e:
                message = "Error contacting with the Gateway"
                response = JsonResponse({
                    'status': 'false',
                    'message': message
                })
                response.status_code = 418
                logger.error(e)
                return response
            else:
                post_params = {
                    "payment_amount":
                        decimal.Decimal(transaction.amount).quantize(
                            decimal.Decimal('0.00000001'),
                            rounding=decimal.ROUND_DOWN).normalize(),
                    "payment_address":
                        transaction.address,
                    "payment_qr":
                        transaction.qrcode_url,
                    "gateway_status":
                        transaction.status_url,
                    "policy_cover":
                        policy.cover,
                    "exchange_name":
                        policy.exchange.name,
                    "date_of_formating":
                        policy.request_date.date(),
                    "currency":
                        currency
                }

                response = JsonResponse(post_params)
                return response
        else:
            # payment already exist
            if payment.status == PaymentStatus.ERROR:
                logger.info('status Error, should create new')
                post_params = {
                    'amount': policy.fee,
                    'currency1': 'BTC',
                    'currency2': currency,
                    'buyer_email':
                        request.user.email,  # TODO set request.user.mail,
                    'item_name': 'Policy for ' + policy.exchange.name,
                    'item_number': policy.id
                }

                try:
                    client = CryptoPayments(public_key, private_key)
                    transaction = client.createTransaction(post_params)
                except Exception as e:
                    logger.error(e)
                    message = 'Payment gateway is down'
                    responseData = {'error': True, 'message': message}
                    return JsonResponse(responseData)

                try:
                    payment = UserPayments(
                        status=0,
                        update_date=datetime.datetime.now(),
                        amount=transaction.amount,
                        address=transaction.address,
                        payment=transaction.txn_id,
                        confirms_needed=transaction.confirms_needed,
                        timeout=transaction.timeout,
                        status_url=transaction.status_url,
                        qrcode_url=transaction.qrcode_url,
                        currency=currency)
                    payment.save()
                    policy.payment_id = payment
                    policy.save()

                    try:
                        default_email = os.environ.get('DJANGO_EMAIL_DEFAULT_EMAIL')
                        subject = "Cryptoins: You’re one step away from being secured"
                        message = render_to_string('first_email.html', {'user': policy.user, 'payment': payment})
                        send_mail(subject, message, default_email, [policy.user.email])
                    except Exception:
                        logger.error('Error on sending first email')


                except Exception as e:
                    message = "Error contacting with the Gateway"
                    response = JsonResponse({
                        'status': 'false',
                        'message': message
                    })
                    response.status_code = 418
                    logger.error(e)
                    return response
                else:
                    post_params = {
                        "payment_amount":
                            decimal.Decimal(transaction.amount).quantize(
                                decimal.Decimal('0.00000001'),
                                rounding=decimal.ROUND_DOWN).normalize(),
                        "payment_address":
                            transaction.address,
                        "payment_qr":
                            transaction.qrcode_url,
                        "gateway_status":
                            transaction.status_url,
                        "policy_cover":
                            policy.cover,
                        "exchange_name":
                            policy.exchange.name,
                        "date_of_formating":
                            policy.request_date.date(),
                        "currency":
                            currency
                    }

                    response = JsonResponse(post_params)
                    return response

                    message = "Payment Exist"
                    response = JsonResponse({
                        'status': 'false',
                        'message': message
                    })
                    return response
            elif payment.status == PaymentStatus.PENDING:
                logger.info('status Pending, do nothing')
                transaction = policy.payment_id
            elif payment.status == PaymentStatus.SUCCESS:
                logger.info('status Success')
                transaction = policy.payment_id
            post_params = {
                "payment_amount":
                    decimal.Decimal(transaction.amount).quantize(
                        decimal.Decimal('0.00000001'),
                        rounding=decimal.ROUND_DOWN).normalize(),
                "payment_address":
                    transaction.address,
                "payment_qr":
                    transaction.qrcode_url,
                "gateway_status":
                    transaction.status_url,
                "policy_cover":
                    policy.cover,
                "exchange_name":
                    policy.exchange.name,
                "date_of_formating":
                    policy.request_date.date(),
                "currency":
                    currency
            }

            response = JsonResponse(post_params)
            return response

        
@staff_member_required
def backup_to_csv(request):
    data = {}
    data['referral'] = ReferralPartner
    data['user'] = UserProfile
    data['exchange'] = CryptoExchange
    data['payments'] = UserPayments
    data['policy'] = InsurancePolicy
    data['case'] = InsuranceCase
    data['additional'] = AdditionalData
    cursor = connection.cursor()
    cursor.execute('''SELECT insurance_policy.id AS Policy_number,
                        insurance_policy.request_date AS Policy_date,
                        user_profile.first_name AS First_name,
                        user_profile.last_name AS Last_name,
                        user_profile.email AS Email,
                        insurance_policy.start_date AS Start_date,
                        insurance_policy.expiration_date AS Expiration_date,
                        insurance_policy.expiration_date - \
                        insurance_policy.start_date AS Number_of_days,
                        crypto_exchange.name AS Crypto_exchange_name,
                        crypto_exchange.coverage_limit AS Limit_BTC,
                        insurance_policy.cover AS Insured_Limit,
                        insurance_policy.fee AS Premium_paid,
                        user_payments.amount AS User_paid,
                        user_payments.currency AS User_currency,
                        crypto_exchange.rate AS Premium_rate,
                        user_payments.update_date AS Premium_payment_date,
                        insurance_case.loss_value AS Outstanding_claim_BTC,
                        insurance_case.incident_date AS Date_of_claim,
                        insurance_case.refund_paid AS Paid_claim_BTC,
                        insurance_case.request_date AS Date_of_claim_payment,
                        insurance_policy.status AS Insurance_policy_status,
                        user_payments.status AS User_payments_status,
                        insurance_case.status AS Insurance_case_status
                        FROM insurance_policy
                        LEFT JOIN user_profile ON user_profile.id = \
                        insurance_policy.user
                        LEFT JOIN crypto_exchange ON crypto_exchange.id = \
                        insurance_policy.exchange
                        LEFT JOIN user_payments ON user_payments.id = \
                        insurance_policy.payment_id
                        LEFT JOIN insurance_case ON \
                        insurance_case.insurance = insurance_policy.id
                        ''')
    insurance_report = cursor.fetchall()

    if request.method == 'GET':
        datasets = {}
        datasets['referral'] = not bool(request.GET.get('referral'))
        datasets['user'] = not bool(request.GET.get('user'))
        datasets['exchange'] = not bool(request.GET.get('exchange'))
        datasets['payments'] = not bool(request.GET.get('payments'))
        datasets['policy'] = not bool(request.GET.get('policy'))
        datasets['case'] = not bool(request.GET.get('case'))
        datasets['additional'] = not bool(request.GET.get('additional'))
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=backup.csv.zip'
        z = zipfile.ZipFile(response, 'w')
        for key in datasets:
            if datasets[key] is True:
                output = StringIO()
                writer = csv.writer(output, dialect='excel')
                query = data[key].objects.all().values()
                if query.count() > 0:
                    keys = list(query[0])
                    writer.writerow(sorted(keys))
                    for row in query:
                        writer.writerow([row[k] for k in sorted(keys)])
                else:
                    writer.writerow(['NULL TABLE'])
                z.writestr("%s.csv" % key, output.getvalue())

        out = StringIO()
        writer = csv.writer(out)
        header = [
            'Policy_number', 'Policy_date', 'Name', 'Surname', 'E-mail',
            'Policy_start_date', 'Policy_expiry_date', 'Number_of_days',
            'Crypto_exchange_name', 'Limit_BTC',  'Insured_Limit', 'Premium_paid_BTC',
            'User_paid', 'User_currency', 'Premium_rate_%',
            'Premium_payment_date', 'Outstanding_claim_BTC', 'Date_of_claim',
            'Paid_claim_BTC', 'Date_of_claim_payment',
            'Insurance_policy_status', 'User_payments_status',
            'Insurance_case_status'
        ]

        writer.writerow(header)
        for row in insurance_report:
            writer.writerow(row)
        z.writestr("insurance_report.csv", out.getvalue())
        try:
            if not z.testzip():
                responseData = {'error': True, 'message': 'Nothing to backup'}
                return JsonResponse(responseData)
        except Exception:
            return response
