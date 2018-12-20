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
                        subject = "Website: You’re one step away from being secured"
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
                        subject = "Website: You’re one step away from being secured"
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

@csrf_protect
@login_required
def dashboard(request):
    user = get_object_or_404(
        UserProfile, django_user_id=request.user.id
    )  # django_user because we're searching in the registred users

    # check for referral user
    try:
        userPartner = Partner.objects.get(
            django_user=request.user.id)
        logger.info(
            "Partner: %s logged into system" % (userPartner))
        return account(request)
    except ObjectDoesNotExist:
        # handle case for regular user
        pass

    insurancy_policy_info = Policy.objects.order_by('-id').filter(
        user=user.id).exclude(status=PolicyStatus.DELETED)
    DEFAULT_VALUE = "NOT FOUND"
    PERIOD_NOT_IDENTIFIED = "NOT SET UNTIL PAYMENT DONE"
    PAYMENT_ERROR = "REPEAT PAYMENT"
    # NOTE: Getting every {'fee':value} pair so we could use it
    # while filling the form
    try:
        found_fee_values = insurancy_policy_info.values('fee')
    except Exception:
        logger.error("Fee values hasn't been found for user with ID: " +
                     str(user.id))
        found_fee_values = []

    fee_values = []
    for current_fee_json in found_fee_values:
        fee_values.append(current_fee_json)

    # NOTE: Getting every policy's numbers
    policy_numbers = []
    try:
        found_policy_numbers = insurancy_policy_info.values('id')
    except KeyError as error:
        logger.error("Policy number hasn't been found for user with ID: " +
                     str(user.id))
        found_policy_numbers = []

    for current_policy_number_json in found_policy_numbers:
        policy_numbers.append(current_policy_number_json)

    # NOTE: filling 'insurance period' form

    try:
        found_start_dates = insurancy_policy_info.values('start_date')
    except KeyError as error:
        logger.error("Couldn't find start dates for user with ID: " +
                     str(user.id))
        found_start_dates = []

    start_dates = []
    for current_date in found_start_dates:
        start_dates.append(current_date)

    try:
        found_expiration_dates = insurancy_policy_info.values(
            'expiration_date')
    except KeyError as error:
        logger.error("Couldn't find expirations dates for user with ID: " +
                     str(user.id))
        found_expiration_dates = []

    expiration_dates = []
    for current_date in found_expiration_dates:
        expiration_dates.append(current_date)

    # NOTE: filling 'Limit of liability' form
    try:
        found_limits_of_liability = insurancy_policy_info.values('cover_btc')
    except KeyError as error:
        logger.error("Couldn't find limits of liability for user with ID: " +
                     str(user.id))
        found_limits_of_liability = []

    limits_of_liability = []
    for current_limit in found_limits_of_liability:
        limits_of_liability.append(current_limit)

    # NOTE: filling 'date of formatting' form
    try:
        found_dates_of_formatting = insurancy_policy_info.values(
            'request_date')
    except KeyError as error:
        logger.error("Couldn't find dates of formatting for user with ID: " +
                     str(user.id))
        found_dates_of_formatting = []

    dates_of_formatting = []
    for current_date_of_formatting in found_dates_of_formatting:
        dates_of_formatting.append(current_date_of_formatting)

    # NOTE: filling "Crypto exchange" form
    try:
        found_stock_exchanges = insurancy_policy_info.values('exchange')
    except KeyError as error:
        logger.error("Couldn't find stock exchanges for user with ID: " +
                     str(user.id))
        found_stock_exchanges = []

    stock_exchange_ids = []
    for current_stock_exchange_id in found_stock_exchanges:
        stock_exchange_ids.append(current_stock_exchange_id)

    # NOTE: Filling "Status" form
    try:
        found_policy_statuses = insurancy_policy_info.values('status')
    except KeyError as error:
        logger.error("Couldn't find policy statuses for user with ID: " +
                     str(user.id))
        found_policy_statuses = []

    policy_statuses = []
    for policy_status in found_policy_statuses:
        policy_statuses.append(policy_status)

    contextPolicy = []
    for current_id, policy_id in enumerate(insurancy_policy_info):

        context_policy_number = DEFAULT_VALUE
        context_limit = DEFAULT_VALUE
        context_date_of_formatting = DEFAULT_VALUE
        context_insurance_period = PERIOD_NOT_IDENTIFIED
        context_fee = DEFAULT_VALUE
        context_stock_exchange = DEFAULT_VALUE

        # NOTE: filling policy number
        policy_number_tag = "Crypto"
        try:
            context_policy_number = policy_number_tag + \
                                    str((policy_numbers[current_id])['id'])
        except (IndexError, KeyError) as error:
            logger.error(
                "An error has occured while trying to get policy number.\
                Reason: " + str(error))

        # NOTE: filling 'Amount of premium' form
        try:
            context_fee = fee_values[current_id]['fee']
        except (IndexError, KeyError) as error:
            logger.error(
                "An error has occured while trying to get fee. Reason: " +
                str(error))

        # NOTE: filling 'insurane period' form
        try:
            s_date = start_dates[current_id]['start_date']
            e_date = expiration_dates[current_id]['expiration_date']
            context_insurance_period = '%s %s\'%s - %s %s\'%s' % (
                s_date.day, s_date.strftime("%B")[0:3], s_date.year - 2000,
                e_date.day, e_date.strftime("%B")[0:3], e_date.year - 2000)
        except (IndexError, KeyError, AttributeError) as error:
            if policy_id.payment_id and policy_id.payment_id.status < 0:
                context_insurance_period = PAYMENT_ERROR
                logger.error(
                    "An error has occured while trying to get insurane period.\
                    Reason: " + str(error))

        # NOTE: filling 'Limit of liability' form
        try:
            context_limit = limits_of_liability[current_id]['cover_btc']
        except (IndexError, KeyError) as error:
            logger.error(
                "An error has occured while trying to get limit . Reason: " +
                str(error))

        # NOTE: filling 'date of formatting' form
        try:
            context_date_of_formatting = str(
                dates_of_formatting[current_id]['request_date'].date())
        except (IndexError, KeyError, AttributeError) as error:
            logger.error(
                "An error has occured while trying to get date of formatting.\
                Reason: " + str(error))

        # NOTE: filling "Crypto exchange" form
        try:
            exchange_tag = CryptoExchange.objects.filter(id=stock_exchange_ids[
                current_id]['exchange']).values('name')[0]
            context_stock_exchange = exchange_tag['name']
        except (IndexError, KeyError) as error:
            logger.error(
                "An error has occured while trying to get exchange tag.\
                Reason: " + str(error))

        # NOTE: filling "policy status" form

        try:
            policy_status_numerical_value = policy_statuses[current_id][
                'status']
            policy_status_tag = get_policy_status_tag(
                policy_status_numerical_value)
        except (IndexError, KeyError) as error:
            logger.error(
                "An error has occured while trying to get policy status.\
                Reason: " + str(error))

        sos = False
        try:
            sosexists = InsuranceCase.objects.filter(
                insurance=(policy_numbers[current_id])['id'])
            logger.debug(sosexists.count())
            if sosexists.count() > 0:
                sos = True
        except (IndexError, KeyError) as error:
            logger.error(
                "An error has occured while trying to get InsuranceCase.\
                Reason: " + str(error))
        if start_dates[current_id]['start_date']:
            days = expiration_dates[current_id]['expiration_date'] -\
                timezone.make_aware(
                datetime.datetime.now())
            if policy_status_numerical_value == 2 and (
                    days < datetime.timedelta(days=10)):
                expired_soon = True
                days_left = int(
                    (expiration_dates[current_id]['expiration_date'] -
                     timezone.make_aware(datetime.datetime.now())).days) + 1
            else:
                expired_soon = False
                days_left = None
        else:
            expired_soon = False
            days_left = None

        context_policies = {
            'id': (policy_numbers[current_id])['id'],
            'policy_number':
            context_policy_number,
            'insurance_period':
            context_insurance_period,
            'limit':
            context_limit,
            'stock':
            context_stock_exchange,
            'formatting_date':
            context_date_of_formatting,
            'amount_of_premium':
            decimal.Decimal(context_fee).quantize(
                decimal.Decimal('0.00000001'),
                rounding=decimal.ROUND_DOWN).normalize(),
            'status':
            policy_status_tag,
            'numstatus':
            policy_status_numerical_value,
            'sosexists':
            sos,
            'expired_soon':
            expired_soon,
            'days_left':
            days_left
        }
        logger.debug(context_policies)
        contextPolicy.append(context_policies)

    # Check User
    # ..........
    # If user
    # Get User policies and notifications
    # Policies model:
    # - Id - unique. Need to identify a policy(to get info page).
    # Mb we can use another field("Policy number"?)
    # - Policy number
    # - Insurance period
    # - Limits of liability
    # - Crypto exchange
    # - Date of formation
    # - Amount of premium paid
    # Notification model:
    # - Text
    # - Date


# POLICY_STATUS_ACTIVE = 2
# POLICY_STATUS_WAITING_FOR_PAYMENT = 4
    stock_exchange_tags = set()
    for stock_exchange in stock_exchange_ids:
        current_stock_exchange = (CryptoExchange.objects.select_related(
        ).filter(id=stock_exchange['exchange']).values('name')[0])['name']
        stock_exchange_tags.add(current_stock_exchange)

    user_limit_information_context = []
    for stock_exchange in stock_exchange_tags:
        coverage_limit = (CryptoExchange.objects.select_related().filter(
            name=stock_exchange).values('coverage_limit')[0])['coverage_limit']
        # current_stock_exchange = (CryptoExchange.objects.select_related(
        # ).filter(id=stock_exchange['exchange']).values('name')[0])['name']
        current_stock_exchange = stock_exchange
        amount_of_holdings = 0
        for policy in contextPolicy:
            if policy['stock'] == current_stock_exchange and (
                    policy['numstatus'] == 1
                    or policy['numstatus'] == 2):  # BEFORE 2
                amount_of_holdings += float(policy['limit'])
        user_limit_information = {
            'stock_exchange': current_stock_exchange,
            'summary_of_holdings': amount_of_holdings,
            'coverage_limit': float(coverage_limit),
            'rate': int(amount_of_holdings / float(coverage_limit) * 100)
        }
        user_limit_information_context.append(user_limit_information)
        logger.debug(contextPolicy)
    # user_limit_information_context = set(user_limit_information_context)
    context = {
        'USER_LIMIT_INFO': user_limit_information_context,
        'POLICIES': contextPolicy,
        # ToDo:
        # Check if user already referral partern
        'is_referral': False
    }
    return render(request, 'website/dashboard/dashboard.html', context)
