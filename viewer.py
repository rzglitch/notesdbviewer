from flask import Flask, render_template, send_from_directory
import sqlite3
import gzip
import datetime

notes_dir = "AppDomainGroup-group.com.apple.notes"
con = sqlite3.connect("./" + notes_dir + "/NoteStore.sqlite",
                      check_same_thread=False)


def getHumanReadableDateTime(time: int):
    time = time + 978307200
    conv_str = datetime.datetime.utcfromtimestamp(int(time))

    return conv_str


def getFolderList(page: int):
    cur = con.cursor()
    real_page = page - 1

    res = cur.execute("SELECT Z_PK, ZFOLDERTYPE, ZTITLE2 " +
                      "FROM ZICCLOUDSYNCINGOBJECT WHERE ZFOLDERTYPE " +
                      "IS NOT NULL ORDER BY Z_PK ASC LIMIT " +
                      str(real_page * 20) + ",20")
    aList = []
    for item in res.fetchall():
        num = item[0]
        foldertype = item[1]
        title = item[2]

        aList.append([num, foldertype, title])

    return aList


def getList(folder: int, page: int):
    cur = con.cursor()
    real_page = page - 1

    res = cur.execute("SELECT ZNOTEDATA, ZSNIPPET, ZTITLE, " +
                      "ZTITLE1, ZCREATIONDATE, ZCREATIONDATE1, " +
                      "ZCREATIONDATE2, ZCREATIONDATE3 FROM " +
                      "ZICCLOUDSYNCINGOBJECT WHERE ZNOTEDATA " +
                      "IS NOT NULL AND ZFOLDER = " + str(folder) + " " +
                      "ORDER BY ZCREATIONDATE3 DESC LIMIT " +
                      str(real_page * 20) + ",20")
    aList = []
    for item in res.fetchall():
        num = item[0]

        title = [item[2], item[3]]
        date = [item[4], item[5], item[6], item[7]]

        for i in title:
            if i is not None:
                title = i

        for i in date:
            if i is not None:
                date = i

        snippet = item[1]

        aList.append([num, title, snippet, getHumanReadableDateTime(date)])

    return aList


def getContent(data_no: int):
    cur = con.cursor()
    cur2 = con.cursor()
    cur3 = con.cursor()
    res = cur.execute("SELECT ZNOTE, ZDATA FROM ZICNOTEDATA WHERE " +
                      "Z_PK=" + str(data_no))
    res_data = res.fetchall()
    data = gzip.decompress(res_data[0][1])
    znote = res_data[0][0]

    res2 = cur2.execute("SELECT Z_PK, ZTITLE, ZTITLE1, " +
                        "ZCREATIONDATE, ZCREATIONDATE1, " +
                        "ZCREATIONDATE2, ZCREATIONDATE3 " +
                        "FROM ZICCLOUDSYNCINGOBJECT WHERE " +
                        "ZNOTEDATA=" + str(data_no))

    res2_data = res2.fetchall()[0]

    title = [res2_data[1], res2_data[2]]
    date = [res2_data[3], res2_data[4],
            res2_data[5], res2_data[6]]

    for i in title:
        if i is not None:
            title = i

    for i in date:
        if i is not None:
            date = i

    # Find attachments
    res3 = cur3.execute("SELECT ZNOTE, ZNOTE1, ZMEDIA, Z_PK, " +
                        "ZIDENTIFIER, ZTITLE, ZFILENAME, " +
                        "ZTYPEUTI, ZTYPEUTI1 FROM ZICCLOUDSYNCINGOBJECT " +
                        "WHERE ZNOTE = "+str(znote)+" OR ZNOTE1 = " +
                        str(znote))

    attachment = []

    for item in res3.fetchall():
        typeuti = [item[7], item[8]]

        for i in typeuti:
            if i is not None:
                typeuti = i

        if item[2] is not None:
            # media exists
            res4 = cur3.execute("SELECT Z_PK, ZIDENTIFIER, ZFILENAME " +
                                "FROM ZICCLOUDSYNCINGOBJECT " +
                                "WHERE Z_PK = "+str(item[2]))
            fetch = res4.fetchall()[0]
            identifier = fetch[1]
            fname = fetch[2]
            attachment.append([identifier, fname, typeuti])
        elif typeuti == "com.apple.drawing.2":
            identifier = item[4]
            attachment.append([identifier, None, typeuti])

    data = data.decode("utf-8", errors='ignore')

    if (title[0:1] in data):
        data = title[0:1] + data.split(title[0:1], 1)[1]
        data = data.split("\x1a\x10")[0]
        data = data.replace("\n", "<br />")

        replace_bytes = bytes.fromhex('efbfbc')
        replace_from = replace_bytes.decode('utf-8')

        for item in attachment:
            replace_to = ""

            if item[2] == "com.apple.drawing.2":
                replace_to = "<img src=\"/getDrawingObject/" + item[0] + "\">"
            else:
                replace_to = "<a href=\"/getAttachmentObject/" + item[0]
                replace_to += "\">" + item[1] + "</a>"

            data = data.replace(replace_from, replace_to, 1)

        data = data.replace("  ", "&nbsp;&nbsp;")

        return [data, date]
    else:
        for item in attachment:
            attach = ""

            if item[2] == "com.apple.drawing.2":
                attach = "<img src=\"/getDrawingObject/" + item[0] + "\">"
            else:
                attach = "<a href=\"/getAttachmentObject/" + item[0] + "\">"
                attach += item[1] + "</a>"

            title = title + "<br>" + attach

        return [title, date]


def getPagination(page):
    if page < 1:
        page = 1

    prev_page = page - 1
    next_page = page + 1

    if prev_page < 1:
        prev_page = 1

    return {
        "prev_page": prev_page,
        "next_page": next_page
    }


app = Flask(__name__)


@app.route("/")
def folderlist(page=1):
    list = getFolderList(int(page))
    pagination = getPagination(int(page))
    return render_template('listfolder.html', page=page,
                           pagination=pagination, list=list)


@app.route("/folder")
@app.route("/folder/p<page>")
def folderlistwithpage(page=1):
    list = getFolderList(int(page))
    pagination = getPagination(int(page))
    return render_template('listfolder.html', page=page,
                           pagination=pagination, list=list)


@app.route("/list/<folder>/p<page>")
def list(folder=0, page=1):
    list = getList(int(folder), int(page))
    pagination = getPagination(int(page))
    return render_template('list.html', page=page, pagination=pagination,
                           list=list, folder=folder)


@app.route("/view/<folder>/p<page>/<no>")
def view(folder=0, page=1, no=0):
    list = getList(int(folder), int(page))
    content = getContent(int(no))
    pagination = getPagination(int(page))
    return render_template('view.html', page=page, pagination=pagination,
                           list=list, folder=folder, no=int(no),
                           content=content)


@app.route('/getDrawingObject/<uuid>', methods=['GET'])
def download_drawing(uuid):
    return send_from_directory("./" + notes_dir + "/" +
                               "Accounts/LocalAccount/Previews",
                               uuid + "-1-768x768-0.png")


@app.route('/getAttachmentObject/<uuid>', methods=['GET'])
def download_attach(uuid):
    cur = con.cursor()
    query = """SELECT Z_PK, ZIDENTIFIER, ZFILENAME
            FROM ZICCLOUDSYNCINGOBJECT
            WHERE ZIDENTIFIER = ?"""
    res = cur.execute(query, (uuid,))
    fetch = res.fetchall()[0]
    filename = fetch[2]

    return send_from_directory("./" + notes_dir + "/" +
                               "Accounts/LocalAccount/Media/" + uuid,
                               filename)
