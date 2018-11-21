    for item in items:
        bits = []

        try:
            bits.append(str(item['item'].attr_x))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item['item'].attr_x.attr_x))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item['x']))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item['item'].attr_x.attr_x))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item.get('x', '')))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item.get('x', '')))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item.get('x', '')))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item.get('x')))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item.get('x', '')))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item.get('x', '')))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item.get('x', '')))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item.get('x', '')))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item.get('x', '')))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item['create_date'].strftime('%Y-%m-%d')))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item['item'].attr_x))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item['item'].attr_x))
        except:
            bits.append('ERR')

        try:
            if not item['item'].attr_x or item['item'].attr_x is None:
                bits.append('0.00')
            else:
                bits.append(str(item['item'].attr_x))
        except:
            bits.append('ERR')

        try:
            bits.append(str(item['item'].attr_x))
        except:
            bits.append('ERR')
        output.append('"{line}"'.format(line='","'.join([s.replace('"', "'") for s in bits])))
