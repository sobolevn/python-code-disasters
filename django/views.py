@login_required
@transaction.commit_on_success
def create_waybill(request, id):
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
