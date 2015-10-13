def create_objects(name, data, send=False, code=None):
    data = [r for r in data if r[0] and r[1]]
    keys = ['{}:{}'.format(*r) for r in data]
    
    existing_objects = dict(Object.objects.filter(name=name, key__in=keys).values_list('key', 'uid'))

    with transaction.commit_on_success():
        for (pid, w, uid), key in izip(data, keys):
            if key not in existing_objects:
                try:
                    if pid.startswith('_'):
                        result = Result.objects.get(pid=pid)
                    else:
                        result = Result.objects.filter(Q(barcode=pid) | Q(oid=pid)).latest('created')
                except Result.DoesNotExist:
                    logger.info("Can't find result [%s] for w [%s]", pid, w)
                    continue

                try:
                    t = Object.objects.get(name=name, w=w, result=result)
                except:
                    if result.container.is_co:
                        code = result.container.co.num
                    else:
                        code = name_code
                    t = Object.objects.create(name=name, w=w, key=key,result=result, uid=uid, name_code=code)

                    reannounce(t)

                    if result.expires_date or (result.registry.is_sending and result.status in [Result.C, Result.W]):
                        Client().Update(result)

                if not result.is_blocked and not result.in_container:
                    if send:
                        if result.status == Result.STATUS1:
                            Result.objects.filter(id=result.id).update(status=Result.STATUS2, on_way_back_date=datetime.now())
                        else:
                            started(result)

            elif uid != existing_objects[key] and uid:
                t = Object.objects.get(name=name, key=key)
                t.uid = uid
                t.name_code = name_code
                t.save()
                reannounce(t)