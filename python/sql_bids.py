def process_offers(offer, counter_general, counter, counter_update, counter_switched_back):
    def insert_record_to_offers_ml(id, offer_name, platform, tracking_link, geo, app_category, creative_link, icon_link,
                                app_desc,
                                percent_payout, payout_type, preview_link, daily_cap, status):
        c.execute(
            'INSERT OR REPLACE INTO offers (id, offer_name, platform, tracking_link, geo, app_category, creative_link, icon_link, app_desc, percent_payout, payout_type, preview_link, daily_cap, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (id, offer_name, platform, tracking_link, geo, app_category, creative_link, icon_link, app_desc,
             percent_payout, payout_type, preview_link, daily_cap, status))
        conn.commit()

    def update_record_in_offers_ml(field, value, id):
        try:
            if isinstance(value, basestring):
                value = value.decode('utf-8')
            c.execute(
                "UPDATE offers SET " + field + " = ?, updated = 1 WHERE id = ?", (value, id))
            conn.commit()
        except sqlite3.ProgrammingError:
            ipdb.set_trace()

    def update_status_in_offers_ml(field, value, id):
        c.execute(
            "UPDATE offers SET " + field + " = ? WHERE id = ?", (value, id))
        # "UPDATE offers SET " + field + " = ? WHERE id = ?", (value, id))
        conn.commit()

    try:
        if 'bid' in offer and 'externalOfferId' in offer:
            if float(offer['bid']) > 0.15 and float(offer['bid']) < 40.0 and not any_in(restricted_offers_list, offer['name'].lower()):
                counter_general += 1
                with lock2:
                    c.execute(
                    "SELECT id, offer_name, platform, tracking_link, geo, app_category, creative_link, icon_link, app_desc, percent_payout, payout_type, preview_link, daily_cap, status, hasoffer_id FROM offers WHERE id = ?",
                    (offer['externalOfferId'],))
                    success = c.fetchone()
                # if offer['platform'] == "ios":
                #     offer['click_url'] += "&channel={affiliate_id}_{source}&idfa={ios_ifa}&aff_sub={transaction_id}"
                # else:
                #     offer['click_url'] += "&channel={affiliate_id}_{source}&andid={android_id}{google_aid}&aff_sub={transaction_id}"

                # offer['click_url'] = re.sub(r"\{sub\}", "{transaction_id}", offer['click_url'])
                # offer['click_url'] = re.sub(r"\{sub_id\}", "{affiliate_id}_{source}",offer['click_url'])
                # offer['click_url'] = re.sub(r"\{idfa\}", "{ios_ifa}", offer['click_url'])
                # offer['click_url'] = re.sub(r"\{gaid\}", "{google_aid}", offer['click_url'])
                # offer['click_url'] = re.sub(r"\{aid\}", "{android_id}", offer['click_url'])
                # offer['click_url'] = re.sub(r"\{imei\}", "{off_imei}", offer['click_url'])

                if '12' in offer['platform']:
                    offer['app_os'] = 'ios'
                    offer['shortenURL'] += "?p1={transaction_id}&subid={affiliate_id}"
                    offer['preview_url'] = 'https://itunes.apple.com/app/id' + offer['packageName']
                else:
                    offer['app_os'] = 'android'
                    offer['shortenURL'] += "?p1={transaction_id}&subid={affiliate_id}"
                    offer['preview_url'] = 'https://play.google.com/store/apps/details?id=' + offer[
                        'packageName']

                creative_string = offer['iconLink']
                icon_link = offer['iconLink']

                offer['country'] = offer['geo']

                if success is None:
                    print "Добавляем " + offer['name'].encode('utf-8') + " " + offer['country'].encode('utf-8')
                    with lock2:
                        insert_record_to_offers_ml(offer['externalOfferId'], offer['name'], offer['app_os'],
                                            offer['shortenURL'], offer['country'],
                                            offer['category'], creative_string,
                                            icon_link, offer['description'] if offer[
                            'description'] else "Default description for all applications",
                                            offer['bid'], "cpa_flat", offer['preview_url'],
                                            offer['daily_capping'], "active")
                    counter += 1
                else:
                    print "Изменяем " + str(offer['externalOfferId']) + " " + offer['name'].encode(
                        'utf-8') + " " + offer['country'].encode('utf-8')
                    if success[3] != offer['shortenURL']:
                        print "Обновлено старое значение tracking link ", str(success[3]), " на новое ", str(
                            offer['shortenURL'])
                        with lock2:
                            update_record_in_offers_ml("tracking_link", offer['shortenURL'], str(success[0]))
                        counter_update += 1
                    if str(success[9]) != str(offer['bid']):
                        print "Обновлено старое значение payout ", str(success[9]), " на новое ", str(
                            offer['bid'])
                        with lock2:
                            update_record_in_offers_ml("percent_payout", offer['bid'], str(success[0]))
                        counter_update += 1
                    if str(success[12]) != str(offer['daily_capping']):
                        print "Обновлено старое значение remaining cap ", str(success[12]), " на новое ", str(
                            offer['daily_capping'])
                        with lock2:
                            update_record_in_offers_ml("daily_cap", offer['daily_capping'], str(success[0]))
                        counter_update += 1
                    if success[13] != "active":
                        print "Обновлено значение статуса с ", str(success[13]), " на ", "active"
                        with lock2:
                            update_status_in_offers_ml("status", "active", str(success[0]))
                        counter_switched_back += 1
        else:
            print "Offer has no bid and no externalOfferId: ", offer
    except TypeError:
        return
