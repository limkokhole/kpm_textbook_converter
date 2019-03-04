import os, sys, re, urllib, hashlib, subprocess
try: from bs4 import BeautifulSoup #, SoupStrainer #python3 #python2 also got, and python need use this or else error when `soup = BeautifulSoup(r, "lxml")` 
except ImportError: from BeautifulSoup import BeautifulSoup #, SoupStrainer #python2

#ensures grep -r amazon first since it might appear some other tags in future
ORIG_TEMPLATE = '''
                <!DOCTYPE html>
		<html><head>
		<script>
			function refreshFrame(id, href) {
				let elem = document.getElementById(id);

				//SecurityError: Permission denied to access property "check_offline" on cross-origin object
				//elem.contentWindow.check_offline = undefined; //some html got this and auto-close offline video

				console.log('src: ' + elem.src);
				console.log('id: ' + id);
				console.log('href: ' + href);
				if (elem.src === 'http://256.256.256.256/' || elem.src === '') {
				    elem.src = href; 
				    elem.style.display = 'block';
				} else {
				    //stop nested iframe video, nid valid path (but can invalid page) to force it refresh
                                    //Firefox can simply put hide:// custom protocol, but Chrome doesn't support it, so need use this invalid ip
				    elem.src = 'http://256.256.256.256/'; 
				    elem.style.display = 'none';
				}
			}
		 </script>
		<style type="text/css"> .box{}
		iframe {
		  display: none;
		  width: 100vw;
		  height: 100vh;
		  max-width: 100%;
		  margin: 0;
		  padding: 0;
		  border: 0 none;
		  box-sizing: border-box;
		}
		</style> </head>
           '''

def check_tag(start_tag, end_tag, r, downloaded_once, cur, fname, http_prefix):
    l = r
    if start_tag + http_prefix in r:
	print(fname + ' tag is ' + start_tag + http_prefix)
	l = r.split(start_tag + http_prefix)
	for i, ll in enumerate(l):
	    if (i == 0): 
		continue
	    if end_tag in ll:
		lll = ll.split(end_tag)
		url =  http_prefix + lll[0]
                ext = os.path.splitext(url)[1].strip().lower()
                download_f = hashlib.md5(url.encode('utf-8')).hexdigest() + ext #prevent multiple same filenames, e.g. index.html of https://s3-ap-southeast-1.amazonaws.com/esdownloadcentre/stu_media/geografit1/geo-kulitver5.iframe/index.html
		download_path = os.path.join( cur, download_f )
                if ( ('.vimeo.com/' in url) or ('.youtube.com/' in url) ):
                   #if ( bool( re.match('^[a-zA-Z0-9:/.#?&=%]+$', 'http://google.com/123abc#?&=%') ) )
                    url = url.replace('&amp;', '&') #no nid care 'a&amp;amp;C'
                    if not ( bool( re.match('^[a-zA-Z0-9:/.#?&=%_-]+$', url) ) ): #prevent crafted url
                        #https://player.vimeo.com/video/263285297?title=0&amp;byline=0&amp;portrait=0&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=109149 into ./OEBPS/746738309168b7183615b0b8681f6bc7
                        #http://www.youtube.com/watch?v=4pnxzrbB-eU
                        print('strange video url, pls check')
                        print('Downloading url '  + url + ' into ' + download_path)
                        sys.exit(1)
                    if start_tag != ' xsrc="': #xsrc not working for video, must src
                            download_f += '.mp4'
                            download_path = os.path.join( cur, download_f )
                            print('Downloading... '  + url + ' into ' + download_path)
			    #download_path = os.path.join( cur, '%(title)s-%(upload_date)s-%(id)s.%(ext)s' ) #lazy to move again to write to html
			    command = 'youtube-dl  -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4" -c --no-mtime -o "' + download_path + '" ' + url  #ensures got youtube-dl command #don't know how to predict downloaded ext, the fastest way is specify mp4 only
			    print('download video: ' + repr(command))
			    proc = subprocess.Popen(command, shell=True, bufsize=2048, stdout=subprocess.PIPE, close_fds=True)
			    http_code = proc.stdout.read()
			    try:
				proc.communicate() #wait for complete
			    except Exception, e:
				print "proc exception ", e #[Errno 10] No child processe
                elif ( ('google.com/maps/' in url) or ('bing.com/maps/' in url) ): 
                    #https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d3983.7649121595014!2d101.69051999999999!3d3.156574!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31cc482e1dd85607%3A0x99e5b5fe4bc9e5ce!2sMemorial+Tunku+Abdul+Rahman!5e0!3m2!1sen!2s!4v1404407745969
                    download_f = url
                else:
                    download_path = os.path.join( cur, download_f )
                    print('Downloading... '  + url + ' into ' + download_path)
		    urllib.urlretrieve(url, download_path)
		print('Downloaded: ' + download_f)
		if (len(lll) > 1):
		    l[i] = download_f + end_tag + end_tag.join(lll[1:])
		else:
		    l[i] = download_f + end_tag
		print('new [i] ' + l[i])
	l = start_tag.join(l)
	print(l)
	downloaded_once = True
    return downloaded_once, l
    

def walkdir(dirname):
    for cur, _dirs, files in os.walk(dirname):
        template = ORIG_TEMPLATE #reset
        pref = ''
        head, tail = os.path.split(cur)
        while head:
            pref += '---'
            head, _tail = os.path.split(head)
        #print(pref+tail)
        f_total = str(len(files)) #this for 1 depth only
        for fi, f in enumerate(files):
            #print('\n[' +  str(fi) + ' / ' + f_total + ']\n')
            fname = os.path.join(cur, f)
            #print(pref+'---'+f)
            #if fname.endswith('.htmlTESTING'): #TESTING DISABLED
            if fname.endswith('.html') or fname.endswith('.xhtml'):
                print('\n[' +  str(fi) + ' / ' + f_total + ']\n')
                #print('html f: ' + f)
                downloaded_once = False
                r = ''
	        with open(fname, 'r') as myfile:
                    r = myfile.read()

		    downloaded_once, r = check_tag('background-image: url(', ')', r, False, cur, fname, 'http')
		    downloaded_once, r = check_tag(' src="', '"', r, downloaded_once, cur, fname, 'http') #src need for video
		    downloaded_once, r = check_tag(' xsrc="', '"', r, downloaded_once, cur, fname, 'http') #sometime only xsrc
		    downloaded_once, r = check_tag('<img src="', '"', r, downloaded_once, cur, fname, 'http')

                postAppend = False
                if ('check_offline();' in r) and ('check_offline(){ return true; }<' not in r):
                    r+= '<script>function check_offline(){ return true; }</script>'
                    postAppend = True
                    downloaded_once = True;
                
                if ('hide' in r or 'fade' in r) and ('"holeShowHidden()">' not in r):
			r+= '''
			<script>
				 function holeShowHidden() {
				 var elements = document.getElementsByClassName('hide');
				 while(elements.length > 0){
				     elements[0].classList.remove('hide');

				}
				 var elements = document.getElementsByClassName('fade');
				 while(elements.length > 0){
				     elements[0].classList.remove('fade');
				 
				}
				//need remove this to prevent visible items not overlay each other
				 var elements = document.getElementsByClassName('modal');
				 while(elements.length > 0){
				     elements[0].classList.remove('modal');
				 
				}
			}
			</script>
			<button onclick="holeShowHidden()">Show Hidden</button><br />
			'''
                        postAppend = True
			downloaded_once = True;
                if 'overflow: hidden;' in r:
                    r = r.replace('overflow: hidden;', '')
                    downloaded_once = True
                if "css({overflow:'hidden'});" in r: #prevent e.g. Buletin Sejarah Edisi 1_e353194f3b7cd1b75d69c3ab88041985/OEBPS/06_otak.html , got overflow:'hidden which causes scrolling not possible
                    r = r.replace("css({overflow:'hidden'});", "css({overflow:'auto'});")
                    downloaded_once = True
                if downloaded_once:
                    print('downloaded once...')
                    if postAppend:
                        r = r.replace('</html>', '') + '</html>'
	            with open(fname, 'w') as myfile:
                            print('writing....')
                            myfile.write(r)
                            myfile.close()

            elif (f == 'content.opf') or (f == 'package.opf'):
                print('fpath is ' + cur + '##' + fname )
                href_listed = []
                with open(fname, 'r') as myfile:
                    r = myfile.read()
                    soup = BeautifulSoup(r, "lxml")
                    md = soup.find('metadata')
                    if md:
                        t = md.find('dc:title')
                        if t:
                            template += 'Subject: ' + t.getText()
                        t = md.find('dc:language')
                        if t:
                            template += ' Language: ' + t.getText()
                        t = md.find('dc:publisher')
                        if t:
                            template += ' Publisher: ' + t.getText()
                        t = md.find('dc:date')
                        if t:
                            template += ' Date: ' + t.getText()
                    #template += '<br/ ><br />Tip: If you want watch only single video, simply right-click video -> Copy Video Location -> click "refresh" button to toggle off noise -> paste link into new tab. Don\'t choose "View Video" since it still require to click correct "refresh" button when back, to toggle off video run in background.<br /><br />'
                    template += '<br/ ><br />Tip 1: If bottom left button "Show Hidden" exist, then you can click to see hidden item such as video running in background. You should click this button without click any video in that page yet.<br />Tip 2: Click toggle button can refresh the page.<br />Tip 3: Try click URL bar and press Enter to refresh the window if audio not off when back from new page.<br />Tip 4: You can right-click on video and choose "Full Screen"(Firefox) or "Copy Video Address" to paste in new tab<br />Tip 5: If you see google.com error, then you may need internet connection to navigate Google map.<br />Tip 6: Press F11 to toggle full screen, press Ctrl- and Ctrl+ to zoom<br /><br />'
                    data = soup.findAll('item')
                    #print('data: ' + repr(data))
                    if data:
                        for dat in data:
                            href = dat.get('href').strip()
                            if href.endswith('.html') or href.endswith('.xhtml'): #exclude image/js/xml/woff
                                item_id = dat.get('id')
                                href_listed.append( os.path.join(cur, href) )
                                href_before = href
                                href = os.path.join('OEBPS', href_before)
                                print('href: ' + href + ' #id: ' + item_id)
                                item_changed = '<input type="button" value="toggle ' + '.'.join(href_before.split('.')[:-1]) + '"  onclick="refreshFrame(\'' + item_id + '\', \'' + href + '\')"><iframe id="' + item_id + '" media-type="image/jpeg" frameborder="0" scrolling="yes" width="100%"></iframe><br />'
                                #item_changed = '<input type="button" value="refresh ' + '.'.join(href.split('.')[:-1]) + '"  onclick="refreshFrame.call(this)"><iframe id="' + item_id + '" src="' + href + '" media-type="image/jpeg" frameborder="0" scrolling="yes" width="100%"></iframe>'
                                print('after: ' + item_changed)
                                template += item_changed

                printed_unlisted_once = False
                for cur_unlisted, _dirs_unlisted, files_unlisted, in os.walk(cur):
                    f_total_unlisted = str(len(files_unlisted))
                    for fi_unlisted, f_unlisted in enumerate(files_unlisted):
                        #print('\n[Extra: ' +  str(fi_unlisted) + ' / ' + f_total_unlisted + ']\n')
                        fname_unlisted = os.path.join(cur_unlisted, f_unlisted)
                        if fname_unlisted.endswith('.html') or fname_unlisted.endswith('.xhtml'):
                            if (fname_unlisted not in href_listed) and (f_unlisted != 'content.html'):
                                if not (printed_unlisted_once):
                                    printed_unlisted_once = True 
                                    print("cur_unlisted: " + cur_unlisted) 
                                #print("fnamef_unlisted: " + fname_unlisted)
                                #print("fnamef_unlisted: " +  cur.replace(fname_unlisted))
                                h_unlisted_before = fname_unlisted[len(cur) + len(os.sep):] #e.g input: ./Edit F1-Matematik_f1a97397bd2376e27e2eaeb112228118/OEBPS/widget/103178_1/index.html #example output: widget/103178_1/index.html
                                h_unlisted = os.path.join('OEBPS', h_unlisted_before) 
                                print('h before: ' + fname_unlisted) 
                                print('h unlisted:' + h_unlisted)
                                item_id_unlisted = hashlib.md5(h_unlisted.encode('utf-8')).hexdigest()
                                item_added = '<input type="button" value="toggle Attachment: ' + '.'.join(h_unlisted_before.split('.')[:-1]) + '"  onclick="refreshFrame(\'' + item_id_unlisted + '\', \'' + h_unlisted + '\')"><iframe id="' + item_id_unlisted + '" media-type="image/jpeg" frameborder="0" scrolling="yes" width="100%"></iframe><br />'
                                #print('unlisted after: ' + item_added)
                                template += item_added	

                template += '</html>'
                #get parent dir (take care of trailing slash, '', and '.'): https://stackoverflow.com/a/25669963/1074998
                with open( os.path.join( os.path.normpath(os.path.join(cur, os.pardir)) , 'content.html'), 'w') as myfile:
                    print('writing toc in html')
                    myfile.write(template)
                    myfile.close()

walkdir('.')

