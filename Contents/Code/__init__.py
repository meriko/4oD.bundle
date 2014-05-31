TITLE  = '4oD'
PREFIX = '/video/4odmobile'
ART    = R('art-default.jpg')
ICON   = R('icon-default.png')

BROKEN_TITLE   = "This channel is no longer available"
BROKEN_MESSAGE = "Due to updates of the 4oD website, this channel is no longer available. Don't expect any update soon since it is not an easy fix ..."

###################################################################################################
def Start():
    ObjectContainer.title1 = TITLE
    ObjectContainer.art    = ART

    DirectoryObject.thumb = ICON

###################################################################################################
@handler(PREFIX, TITLE, art = ART, thumb = ICON)
def MainMenu():
    oc = ObjectContainer(no_cache = True)
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Broken
                ),
            title   = BROKEN_TITLE,
            summary = BROKEN_MESSAGE
        )
    )

    return oc
    
####################################################################################################
@route(PREFIX + '/Broken')
def Broken():
	oc = ObjectContainer(title2 = "Broken")
	
	oc.header  = BROKEN_TITLE
	oc.message = BROKEN_MESSAGE
	
	return oc
