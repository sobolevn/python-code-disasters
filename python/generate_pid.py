class Generator(MasterClass):
    def generate_pid(self):
        from .models import PidCounter, PID

        today = date.today()
        datestr = "{0.day:02}{0.month:02}{1}".format(today, str(today.year)[-1])

        counter, _ = PidCounter.objects.get_or_create(date=today)

        counter.counter += 1
        counter.save()

        num = "{0:04}".format(counter.counter)

        nnc = 'PREFIX{0}{1}{2}{3}'.format("%04d" % int(self.account.id), datestr, num, self.sender.id)
        checksum1 = nnc[-2]
        checksum2 = 0 + (1 + 2 + int(nnc[4]) + int(nnc[6]) + int(nnc[8]) + int(nnc[10]) + int(nnc[12]) + int(nnc[14])+ int(nnc[16]) + int(nnc[18]) + int(nnc[20])) * 4
        checksum3 = 0 + int(nnc[3]) + int(nnc[5]) + int(nnc[7]) + int(nnc[9]) + int(nnc[11]) + int(nnc[13]) + int(nnc[15]) + int(nnc[17]) + int(nnc[19] + int(nnc[21])) * 7
        checksum4 = checksum2 + checksum3
        checksum = 0
        while (checksum4 + checksum) % 10:
            checksum += 1

        nc = "{0}{1}".format(nnc, checksum)
        try:
            PID.objects.get(pid=nc)
            nc = self.generate_pid()
        except PID.DoesNotExist:
            return nc