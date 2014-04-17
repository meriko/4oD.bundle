TITLE  = '4oD'
PREFIX = '/video/4odmobile'
ART    = R('art-default.jpg')
ICON   = R('icon-default.png')

RE_EPISODE_DETAILS  = Regex(' *Episode *([0-9]+)')
RE_SERIES_DETAILS   = Regex(' *Series *([0-9]+)')
RE_DURATION_DETAILS = Regex(' *\(([0-9]+)min\)')
RE_PATH_DETAILS     = Regex('/programmes/images(/.*/series-[0-9]+/)')
RE_CATEGORIES       = Regex('\<a *href="(.*)"\>(.*).*')

USER_AGENT = 'Mozilla/5.0 (Linux; U; Android 2.3.5; en-gb; HTC Vision Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'

BASE_URL       = "http://m.channel4.com"
START_URL      = BASE_URL + "/4od/"
CATCHUP_URL    = BASE_URL + "/4od/catchup/%s/allChannels"
CATEGORIES_URL = BASE_URL + "/4od/tags/"
CATEGORY_URL   = BASE_URL + "/4od/tags/%s/%s/"
A_TO_Z_URL     = BASE_URL + "/4od/atoz/%s/"
SEARCH_URL     = BASE_URL + "/4od/search/ajax/%s"

###################################################################################################
def Start():
    ObjectContainer.title1 = TITLE
    ObjectContainer.art    = ART

    DirectoryObject.thumb = ICON
    
    HTTP.CacheTime             = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = USER_AGENT

###################################################################################################
@handler(PREFIX, TITLE, art = ART, thumb = ICON)
def MainMenu():
    oc = ObjectContainer(no_cache = True)
    
    title = 'Recently Added'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Episodes,
                    title = title,
                    url = START_URL
                ),
            title = title
        )
    )
    
    title = 'Recommended'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Recommended,
                    title = title
                ),
            title = title
        )
    )
    
    title = 'Catchup'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Catchup,
                    title = title
                ),
            title = title
        )
    )
    
    title = 'Categories'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Categories,
                    title = title
                ),
            title = title
        )
    )
    
    title = 'A - Z'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    AToZ, 
                    title = title
                ),
            title = title
        )
    )

    title = 'Search'
    oc.add(
        InputDirectoryObject(
            key = Callback(Search, title = title),
            title  = title,
            prompt = title,
            thumb = ICON
        )
    )
    
    return Container(oc)

####################################################################################################
@route(PREFIX + '/Recommended')
def Recommended(title):
	oc = ObjectContainer(title2 = title)
	
	pageElement = HTML.ElementFromURL(START_URL)
	
	for item in pageElement.xpath("//section[@id='carousel']//li"):
	    link = item.xpath(".//a/@href")[0]
	    
	    if not link.startswith("/4od/"):
	        continue
	        
	    url = BASE_URL + link
	        
	    title = item.xpath(".//a/text()")[0].strip()
	    thumb = item.xpath(".//*/@data-src")[0]
	    
	    oc.add(
	        DirectoryObject(
	            key =
	                Callback(
	                    Episodes,
	                    title = title,
	                    url = url
	                ),
	            title = title,
	            thumb = thumb
	        )
	    )
	    
	return Container(oc)

####################################################################################################
@route(PREFIX + '/Catchup')
def Catchup(title):
	oc = ObjectContainer(title2 = title)

	for i in range(30):
		date = Datetime.Now() - Datetime.Delta(days = i)
		date_key = date.strftime('%Y/%m/%d')
		date_label = date.strftime('%A %d %B')
		
		if i == 0:
		    date_label = 'Today'
		elif i == 1:
		    date_label = 'Yesterday'
		elif i >= 2 and i <= 6:
		    date_label = date_label.split(" ")[0]

		oc.add(
		    DirectoryObject(
			    key = 
			        Callback(
			            Episodes,
			            title = date_label,
			            url = CATCHUP_URL % date_key
			        ),
			    title = date_label
		    )
		)

	return Container(oc)
	
####################################################################################################
@route(PREFIX + '/Categories')
def Categories(title):
    oc = ObjectContainer(title2 = title)
    
    content = HTTP.Request(CATEGORIES_URL).content
    
    categories = RE_CATEGORIES.findall(content) # Parsing with HTML doesn't work for this page
    for category in categories:
        link = category[0]
        
        if not link.startswith('/4od/tags/') or link.count("/") != 3:
            continue
        
        title = category[1]
        tag   = link.replace('/4od/tags/', '')
        
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        CategoriesSortChoice,
                        title = title,
                        tag = tag
                    ),
                title = title
            )
        )
    
    return Container(oc)

####################################################################################################
@route(PREFIX + '/CategoriesSortChoice')
def CategoriesSortChoice(title, tag):
    oc = ObjectContainer(title2 = title)
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Shows,
                    url = CATEGORY_URL % (tag, 'latest'),
                    title = title,
                    page = 1
                ),
            title = 'Latest'
        )
    )
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Shows,
                    url = CATEGORY_URL % (tag, 'atoz'),
                    title = title,
                    page = 1
                ),
            title = 'A - Z'
        )
    )
    
    return Container(oc)

####################################################################################################
@route(PREFIX + '/Shows', page = int)
def Shows(url, title, page = None):
    oc = ObjectContainer(title2 = title)
    
    if page:
        dataURL = url + 'page-' + str(page)
    else:
        dataURL = url
    
    shows = JSON.ObjectFromURL(dataURL)
    
    for show in shows['results']:
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Series,
                        url = BASE_URL + show['url'],
                        title = show['title'],
                        thumb = show['img']
                    ),
                title = show['title'],
                thumb = show['img']
            )
        )
        
    if shows['nextPageCount'] > 0:
        oc.add(
            NextPageObject(
                key =
                    Callback(
                        Shows,
                        url = url,
                        title = title,
                        page = page + 1
                    )
            )
        )
    
    return Container(oc)

####################################################################################################
@route(PREFIX + '/Series')
def Series(url, title, thumb):
    oc = ObjectContainer(title2 = title)
    
    pageElement = HTML.ElementFromURL(url)
    
    for item in pageElement.xpath("//li"):
        link = item.xpath(".//a/@href")[0]

        if not url.replace(BASE_URL, "") in link:
            continue
            
        if link.startswith("http") and not link.startswith(BASE_URL):
            continue
        
        finalURL = BASE_URL + link
        try:
            series = int(item.xpath(".//a/text()")[0])
        except:
            series = '?'
            
        finalTitle = 'Series ' + str(series)
        
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Episodes,
                        title = finalTitle,
                        url = finalURL
                    ),
                title = finalTitle,
                thumb = thumb
            )
        )
    
    if len(oc) == 1:
        return Episodes(
            title = finalTitle,
            url = finalURL
        ) 
        
    return Container(oc, message = 'This show is not available')
    
####################################################################################################
@route(PREFIX + '/AToZ')
def AToZ(title):
    oc = ObjectContainer(title2 = title)
    
    for char in list(String.UPPERCASE):
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Shows,
                        url = A_TO_Z_URL % char.lower(),
                        title = char,
                        page = 1
                    ),
                title = char,
            )
        )
        
    return Container(oc) 

####################################################################################################
@route(PREFIX + '/Search')
def Search(query, title):
    oc = Shows(
        url = SEARCH_URL % String.Quote(query).replace("%20", "%2520"),
        title = 'Results for ' + query
    )
    
    return Container(oc, "Could not find any result for '" + query + "'")

####################################################################################################
@route(PREFIX + '/Episodes')
def Episodes(title, url):
    oc = ObjectContainer(title2 = title)
    
    pageElement = HTML.ElementFromURL(url)
    
    for item in pageElement.xpath("//section[@id='episodeList']//article"):
        try:
            id  = item.xpath("./@data-preselectasseturl")[0]
            id  = id[id.rfind("/") + 1:]
            url = BASE_URL + item.xpath(".//div[@class='details']//a/@href")[0]
        except:
            continue
        
        title = item.xpath(".//div[@class='details']//a/text()")[0].strip()          
        thumb = item.xpath(".//img/@src")[0]
        
        if not id in url:
            try:
                url = BASE_URL + '/4od' + RE_PATH_DETAILS.search(thumb).groups()[0] + id
            except:
                continue
                
        lines = ''.join(item.xpath(".//div[@class='details']//p/text()")).strip()
        
        summary = ''
        for line in lines.splitlines():
            if not line.isspace():
                summary = summary + line.strip() + '\r\n'
                
        try:
            episode = int(RE_EPISODE_DETAILS.search(summary).groups()[0])
        except:
            try:
                episode = int(RE_EPISODE_DETAILS.search(item.xpath(".//img/@src")[0]).groups()[0])
            except:
                episode = None
            
        try:
            season = int(RE_SERIES_DETAILS.search(summary).groups()[0])
        except:
            season = None
            
        try:
            duration = int(RE_DURATION_DETAILS.search(summary).groups()[0]) * 60 * 1000
        except:
            duration = None
    
        oc.add(
            EpisodeObject(
                url = url,
                title = title,
                thumb = thumb,
                show = title,
                season = season,
                index = episode,
                summary = summary,
                duration = duration
            )
        )

    return Container(oc)

####################################################################################################
def Container(oc, message = None):
    if len(oc) >= 1:
        return oc
    else:
        oc.header  = "Sorry!"
        
        if message:
            oc.message = message
        else:
            oc.message = "Could not find any content"
            
        return oc
