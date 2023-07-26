use framework "Foundation"
use scripting additions

property NSJSONWritingPrettyPrinted : a reference to 0
property NSJSONSerialization : a reference to current application's NSJSONSerialization

on run
	set cacheDir to system attribute "cachedir"
	set toFile to POSIX file (cacheDir & "/curr_data.json")
	tell application "NetNewsWire"
		tell current article
			set currArticleData to {|title|:title, link:url, |author|:name of the first item of authors, |date|:published date as text, |html|:html}
		end tell
	end tell
	set theJSONData to NSJSONSerialization's dataWithJSONObject:currArticleData options:NSJSONWritingPrettyPrinted |error|:(missing value)
	theJSONData's writeToFile:(toFile's POSIX path) atomically:false
	return
end run