import get_leaf_data as gld
import interpret_match_data as imd


gld.GetLinksToCSV("https://leafapp.co/scrims/310/matches")
imd.ProcessFiles(imd.GetFilesToProcess())
