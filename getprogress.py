import os, time, json, random
from datetime import datetime, timedelta, date

if not os.path.isdir('/tmp/schooltiming/'):
    os.system("mkdir /tmp/schooltiming/")

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

def get_bar(username, password, year, method=1) :
    """
    Return a progress bar of the current school year
    @params:
        username    - Required  : Ecoledirecte username (Str)
        password    - Required  : Ecoledirecte password (Str)
        method      - Required  : style of the bar (0: hours based; 1:classes based) (Int) [default: 1]
        year        - Required  : start of school year (ex: for 2021-2022, enter 2021) (Int)
    """
    year = int(year)
    data = get_data(username=username, password=password)
    if data == False :
        return 'Bad login'
    start = str(year) + '-09-01'
    end = str(year + 1) + '-08-01'
    
    tablestart = Get_time_table(token=data["token"], account_type=data["data"]["accounts"][0]['typeCompte'], id=data["data"]["accounts"][0]['id'], start_date=start, end_date=end, username=username)
    tablenow = Get_time_table(token=data["token"], account_type=data["data"]["accounts"][0]['typeCompte'], id=data["data"]["accounts"][0]['id'], start_date=str(datetime.today()).split()[0], end_date=end, username=username)
    
    if method == 1 :
        total = 0
        for x in range(len(tablestart["data"])):
            if str(tablestart["data"][x]["text"]) != 'CONGÉS' :
                total += 1
        left = 0
        for x in range(len(tablenow["data"])):
            if str(tablenow["data"][x]["text"]) != 'CONGÉS' :
                left += 1
        percentage = ((total-left) / total) * 100
        return [percentage, str(f'{total-left} classes out of {total} ({left} classes left)\t({percentage}%)')]
    if method == 0 :
        total = timedelta()
        for x in range(len(tablestart["data"])):
            if str(tablestart["data"][x]["text"]) != 'CONGÉS' :
                    start=tuple([int(i) for i in str(tablestart["data"][x]["start_date"])[11:].split(':')]) # tuple([int(x) for x in str(tablestart["data"][x]["start_date"])[:10].split('-')])+
                    start = timedelta(hours=start[0], minutes=start[1])
                    end=tuple([int(i) for i in str(tablestart["data"][x]["end_date"])[11:].split(':')]) # tuple([int(x) for x in str(tablestart["data"][x]["end_date"])[:10].split('-')])+
                    end = timedelta(hours=end[0], minutes=end[1])
                    diff = end - start
                    total += diff
        left = timedelta()
        for x in range(len(tablenow["data"])):
            if str(tablenow["data"][x]["text"]) != 'CONGÉS' :
                    start=tuple([int(i) for i in str(tablenow["data"][x]["start_date"])[11:].split(':')]) # tuple([int(x) for x in str(tablestart["data"][x]["start_date"])[:10].split('-')])+
                    start = timedelta(hours=start[0], minutes=start[1])
                    end=tuple([int(i) for i in str(tablenow["data"][x]["end_date"])[11:].split(':')]) # tuple([int(x) for x in str(tablestart["data"][x]["end_date"])[:10].split('-')])+
                    end = timedelta(hours=end[0], minutes=end[1])
                    diff = end - start
                    left += diff
        # return(f'{total-left} of class spent out of {total} ({left} left)')
        spent = total-left
        percentage = (spent.total_seconds() / (total.total_seconds())) * 100
        return [percentage, str(f'{spent} of class out of {total} ({left} of class left)\t({percentage}%)')]
