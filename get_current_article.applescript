use framework "Foundation"
use scripting additions

property NSJSONWritingPrettyPrinted : a reference to 0
property NSJSONSerialization : a reference to current application's NSJSONSerialization

on run
	set cacheDir to system attribute "alfred_workflow_cache"
	set toFile to POSIX file (cacheDir & "/curr_data.json")
	tell application "NetNewsWire"
		tell current article
			set theAuthorNames to {}
			if exists authors then
				set theAuthorNames to name of every author
			end if
			set currArticleData to {|title|:title, link:url, |authors|:theAuthorNames, |date|:published date as text, |html|:html}
		end tell
	end tell
	set theJSONData to NSJSONSerialization's dataWithJSONObject:currArticleData options:NSJSONWritingPrettyPrinted |error|:(missing value)
	theJSONData's writeToFile:(toFile's POSIX path) atomically:false
	return
end run