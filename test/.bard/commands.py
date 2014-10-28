import bard
import os.path
	
def insert(src,dst_root,tags):
	print(src,dst_root,tags)
	
	if('personal' in tags):
		tags.pop('personal')
		return bard.insert(src,os.path.join(dst_root,'personal'),tags)
	if('nsfw' in tags):
		tags.pop('nsfw')
		return bard.insert(src,os.path.join(dst_root,'nsfw'),tags)
	mt=bard.get_mimetype(src)
	
	if('audio' in mt):
		md=bard.read_audio_metatdata(src)
		canonical_name=bard.pathify(os.path.join(md['Genre'],md['Artist'],md['Album'],md['TrackNumber']+md['Title'],'.mp3'))
		cout=dst_root+canonical_name
		if(os.path.exists(os.path.join(cout))):
			mdc=read_metatdata(cout)
			if(mdc['bitrate'] > md['bitrate']):
				return None
				
		return cout,lambda: audio_write(src,cout)
	if('image' in mt):
		md=bard.read_image_metadata(src)
		if(md['width']*md['height'] < 100*100):
			return None
		
		canonical_name=os.path.join('image',md['Timestamp']+md['CameraHash']+md['Img']+'PixelHash','.mp3')
		cout=dst_root+canonical_name
		if(os.path.exists(os.path.join(cout))):
			mdc=read_metatdata(cout)
			if(mdc['bitrate'] > md['bitrate']):
				return None
				
	if('video' in mt):
		pass
		
