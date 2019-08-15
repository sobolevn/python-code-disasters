from multiprocessing import Process

def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts] for i in range(wanted_parts)]

def check_ip(iplist, masklist):
    threads = 16
    workList = {}

    workList[0], workList[1], workList[2], workList[3], \
    workList[4], workList[5], workList[6], workList[7], \
    workList[8], workList[9], workList[10], workList[11], \
    workList[12], workList[13], workList[14], \
    workList[15] = split_list(iplist, 16)

    processes = [
        Process(target=include_worker, args=(workList[i], masklist)) for i
        in range(0, threads)]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
