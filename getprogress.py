import os, time, json, random, re
from datetime import datetime, timedelta, date

if not os.path.isdir('/tmp/schooltiming/'):
    os.system("mkdir /tmp/schooltiming/")

def strToTimedelta(s) :
    days, hours, minutes, seconds = re.match('(?:(\d+) days, )?(\d+):(\d+):([.\d+]+)', s).groups()
    days, hours, minutes, seconds = int(days), int(hours), int(minutes), int(seconds)
    return(timedelta(days=(days or 0), hours=hours, minutes=minutes, seconds=seconds))

def write_json(new_data, filename):
    with open(filename, "r+") as file:
        data = json.load(file)
        if not new_data in data:
            data.append(new_data)
            file.seek(0)
            json.dump(data, file, indent=4, sort_keys=True)
            return("added a new entry")
        else:
            return("entry already existed")

def add_cache(username, path, perecntage1, total1, left1, perecntage2, total2, left2, spent2, next_event) :
    print(f'writing cache for user {username}')
    cache = dict({})
    cache['next_event'] = str(next_event.strftime("%Y-%m-%d %H:%M"))
    print(cache['next_event'])
    cache['percentage1'] = perecntage1
    cache['total1'] = total1
    cache['left1'] = left1
    cache['percentage2'] = perecntage2
    cache['total2'] = str(total2)
    cache['left2'] = str(left2)
    cache['spent2'] = str(spent2)
    os.system(f'rm {path}')
    with open(path, 'x') as f :
        f.seek(0)
        json.dump(cache, f, indent=4, sort_keys=True)


def test_token(token, id) :
    randid = str(random.randint(0,999999))
    command = f'curl --location -g -s --request POST \'https://api.ecoledirecte.com/v3/Eleves/{id}/manuelsNumeriques.awp?verbe=get\' --data-raw \'data={{"token": "{token}"}}\' > /root/code/schooltimeremaining/tokens/tests/{randid}.json'
    print(command)
    os.system(command)
    with open('/root/code/schooltimeremaining/tokens/tests/' + randid + '.json') as f:
        test = json.load(f)
    return test["code"]

def get_data(username, password):
    if not os.path.isfile("/root/code/schooltimeremaining/tokens/data" + username + ".json") :
        os.system(
            "curl -s --location --request POST \'https://api.ecoledirecte.com/v3/login.awp\' --data-raw \'data={\"identifiant\": \"" +
            username + "\", \"motdepasse\": \"" + password +
            "\"}\' > /root/code/schooltimeremaining/tokens/data" + username + ".json"
        )
    else :
        with open('/root/code/schooltimeremaining/tokens/data' + username + '.json') as f:
            data = json.load(f)
        if test_token(data["token"], data["data"]["accounts"][0]["id"]) == 200 :
            return data
        else :
            os.system(
                "curl -s --location --request POST \'https://api.ecoledirecte.com/v3/login.awp\' --data-raw \'data={\"identifiant\": \"" +
                username + "\", \"motdepasse\": \"" + password +
                "\"}\' > /root/code/schooltimeremaining/tokens/data" + username + ".json"
            )
            code = test_token(data["token"], data["data"]["accounts"][0]["id"])
            if code == 200 :
                return data
            else :
                print(code)
                return False
    with open('/root/code/schooltimeremaining/tokens/data' + username + '.json') as f:
        data = json.load(f)
    return data

def test_account(username, password) :
    os.system(
        "curl -s --location --request POST \'https://api.ecoledirecte.com/v3/login.awp\' --data-raw \'data={\"identifiant\": \"" +
        username + "\", \"motdepasse\": \"" + password +
        "\"}\' > /root/code/schooltimeremaining/tokens/data" + username + ".json"
    )
    with open('/root/code/schooltimeremaining/tokens/data' + username + '.json') as f: data = json.load(f)
    if test_token(data["token"], data["data"]["accounts"][0]["id"]) == 200 :
        return 200
    else :
        os.system(
            "curl -s --location --request POST \'https://api.ecoledirecte.com/v3/login.awp\' --data-raw \'data={\"identifiant\": \"" +
            username + "\", \"motdepasse\": \"" + password +
            "\"}\' > /root/code/schooltimeremaining/tokens/data" + username + ".json"
        )
        code = test_token(data["token"])
        return code

def Get_time_table(token, account_type, id, start_date, end_date, username, hole='false'):
    command = (
        "curl -s --location -g -s --request POST \'https://api.ecoledirecte.com/v3/" + str(account_type) + "/" + str(id) + "/emploidutemps.awp?verbe=get\' --data-raw \'data={\"dateDebut\": \"" + str(
            start_date) + "\", \"dateFin\": \"" + str(end_date) + "\", \"avecTrous\": " + str(hole) + ", \"token\": \"" + str(token) + "\"}\' > /tmp/ecoledirecte/timetable" + username + ".json"
    )
    print(command)
    os.system(command)
    with open('/tmp/ecoledirecte/timetable' + username + '.json') as f:
        timetable = json.load(f)
    return timetable

def get_bar(username, password, year, ignoreCache = False) :
    """
    Return a progress bar of the current school year
    @params:
        username    - Required  : Ecoledirecte username (Str)
        password    - Required  : Ecoledirecte password (Str)
        year        - Required  : start of school year (ex: for 2021-2022, enter 2021) (Int)
    """
    if os.path.exists(f'/tmp/schooltiming/cache/{username}.json') and ignoreCache == False :
        with open(f'/tmp/schooltiming/cache/{username}.json') as file: cache = json.load(file)
        print(f'testing cache for user {username}')
        now = datetime.now()
        next_event = tuple([int(x) for x in str(cache["next_event"])[:10].split('-')])+tuple([int(x) for x in str(cache["next_event"])[11:].split(':')])
        if datetime(*next_event) >= now :
            percentage1 = cache['percentage1']
            total1 = cache['total1']
            left1 = cache['left1']
            percentage2 = cache['percentage2']
            total2 = strToTimedelta(cache['total2'])
            left2 = strToTimedelta(cache['left2'])
            spent2 = strToTimedelta(cache['spent2'])
            print(f'using cache for user {username}')
            return [percentage1, str(f'{total1-left1} classes out of {total1} ({left1} classes left)\t({percentage1}%)'), percentage2, str(f'{spent2} of class out of {total2} ({left2} of class left)\t({percentage2}%)')]
    print(f'ignoring cache for user {username}')
    year = int(year)
    data = get_data(username=username, password=password)
    if data == False :
        return 'Bad login'
    start = str(year) + '-09-01'
    end = str(year + 1) + '-08-01'
    table = Get_time_table(token=data["token"], account_type=data["data"]["accounts"][0]['typeCompte'], id=data["data"]["accounts"][0]['id'], start_date=start, end_date=end, username=username)
    total1 = 0
    total2 = timedelta()
    left1 = 0
    left2 = timedelta()
    now = datetime.now()
    next_event = datetime.now()
    for table in table["data"]:
        if str(table["text"]) != 'CONGÉS' :
                start=tuple([int(x) for x in str(table["start_date"])[:10].split('-')])+tuple([int(x) for x in str(table["start_date"])[11:].split(':')])
                start2 = timedelta(hours=start[3], minutes=start[4])
                end=tuple([int(x) for x in str(table["end_date"])[:10].split('-')])+tuple([int(x) for x in str(table["end_date"])[11:].split(':')])
                end2 = timedelta(hours=end[3], minutes=end[4])
                diff = end2 - start2
                if datetime(*end) > now :
                    if datetime(*start) > next_event: next_event = datetime(*start)
                    left2 += diff
                    left1 += 1
                total2 += diff
                total1 += 1
    # return(f'{total-left} of class spent out of {total} ({left} left)')
    spent2 = total2-left2
    percentage1 = ((total1-left1) / total1) * 100
    percentage2 = (spent2.total_seconds() / (total2.total_seconds())) * 100
    add_cache(username=username, path=f'/tmp/schooltiming/cache/{username}.json', perecntage1=percentage1, perecntage2=percentage2, total1=total1, total2=total2, left1=left1, left2=left2, spent2=spent2, next_event=next_event)
    return [percentage1, str(f'{total1-left1} classes out of {total1} ({left1} classes left)\t({percentage1}%)'), percentage2, str(f'{spent2} of class out of {total2} ({left2} of class left)\t({percentage2}%)')]
