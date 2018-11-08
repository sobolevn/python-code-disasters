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
