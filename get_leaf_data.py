import requests
import logging
import os, shutil

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('scrim_requests')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('scrim_requests.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
# logger.propagate = False


def GetMatchFromMatchesTile(tileText):
    return tileText.split("<p class=\"title\">")[1].split("href=")[1].split("\"")[1]


def GetTilesList(scrimURI):
    scrimReq = requests.get(scrimURI)
    linkText = scrimReq.text
    tilesTextArr = linkText.split("tile is-ancestor")
    tilesTextArr.pop(0)

    return tilesTextArr


def GetTimeFromText(timeStr):
    timeStr = timeStr.replace(" ", "").replace("min", "").replace("secs", "")
    splitTime = timeStr.split(",")
    time = (int(splitTime[0]) * 60) + (int(splitTime[1]))
    return time


def GetMatchTimeFromMatchReq(dataReq):
    timeStart = dataReq.text.split('class="tag is-dark">')[1]
    return GetTimeFromText(timeStart.split("<")[0])


def GetMatchScoreFromMatchReq(dataReq):
    scoreOne = dataReq.text.split("class=\"is-pulled-right tag is-danger\">")[1].split("<")[0]
    scoreTwo = dataReq.text.split("class=\"is-pulled-right tag is-info\">")[1].split("<")[0]
    return f"{scoreOne},{scoreTwo}"


def WriteToTextFile(filename, content):
    with open("TempSeriesData\\" + filename, 'w') as f:
        f.write(str(content))


def ExportDataFromMatchURI(matchURI, filename):
    # Add validation

    csvReq = requests.get(matchURI + "/csv")
    open("TempSeriesData\\" + filename, "wb").write(csvReq.content)

def CleanFolder(dir):
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
            return False
    return True


def GetLinksToCSV(scrimURI):
    # Add validation
    logger.info(f"Getting data for scrim: {scrimURI}")
    CleanFolder('TempSeriesData')

    tilesTextArr = GetTilesList(scrimURI)
    for index, tile in enumerate(tilesTextArr):
        matchURI = GetMatchFromMatchesTile(tile)

        filename = f"match_{chr(index + 97)}"
        ExportDataFromMatchURI(matchURI, filename + ".csv")

        dataReq = requests.get(matchURI)
        WriteToTextFile(filename + "_matchtime.txt", GetMatchTimeFromMatchReq(dataReq))
        WriteToTextFile(filename + "_matchscore.txt", GetMatchScoreFromMatchReq(dataReq))
        logger.info(f"Successfully retrieved data from {matchURI}")


# def IsLinkBodyValid(uri):
#     try:
#         data= uri.find("https://leafapp.co/scrims/") != -1
#         cheese = int(uri.split("https://leafapp.co/scrims/")[1].split("/")[0])
#         return True
#     except:
#         return False
