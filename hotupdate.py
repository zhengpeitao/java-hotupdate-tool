#-*-coding:utf-8-*-
import os
import md5
import time
import shutil
import zipfile

#######################################
# ���ã�����maven���������䶯�ļ��Ĵ��
# ԭ�����ļ���¼maven�����������ļ���md5��
#       ÿ�θ��¶Ա���һ�ε�md5���ҵ����б仯���ļ�
# ���ߣ�victor zheng
#######################################


# ����
#######################################
# �ļ�md5��¼
gsPyDigest="md5Digest.txt"
# ��Ŀ��
serverName="video-server-1.17.2"
# ����zip����
zipName=time.strftime("videoserver_hotupdate_%Y%m%d_%H%M.zip",time.localtime())

#######################################


def loopDir(sDir,sNextDir = ""):
	""" ����Ŀ¼ """

	# �ֵ�洢md5��Ϣ|key:�ļ���value:�ļ���Ӧ��md5
	dDigest={}
	sCwd=os.getcwd() +"\\"+ sNextDir

	for sSub in os.listdir(sDir):		
		sNew=os.path.join(sDir,sSub)

		if os.path.isdir(sNew):
			# ������Ŀ¼			
			dDigest.update(loopDir(sNew,sNextDir))
		elif os.path.isfile(sNew):

			sKey=sNew.replace(sCwd+"\\","")
			# ������ֻ����ʽ�����ļ�����
			f=open(sNew,'rb')
			sText=f.read()
			f.close()
			obj=md5.new(sText)			
			dDigest[sKey]=obj.hexdigest()			
	return dDigest




def fullPackage():
	""" ���� """
	targetDir = "target"
	sCwd=os.getcwd() + "\\" + targetDir
	print sCwd
	
	for sSub in os.listdir(targetDir):
		if sSub.endswith(".war"):
			fileName=sSub
			print sSub+"~~~~~~~~~~~~"

	#�ư�
	shutil.move("target/"+fileName,".")
	#������
	os.rename(fileName,"video-server.war")


def hotupdatePackage():
	""" �ȸ��� """

	gtDir = "target\\%s"%(serverName)
	print "compile the results directory:%s"%gtDir

	dNewDigest={}
	fullPath=os.getcwd()+"\\%s"%(gtDir)
	d=loopDir(fullPath, gtDir)
	dNewDigest.update(d)

	# �ɵ��ļ���md5����
	dOldDigest={}
	if os.path.exists(gsPyDigest):

		f=open(gsPyDigest,'r')
		sText=f.read()
		f.close()
		for sLine in sText.splitlines():
			sKey,sValue=sLine.split(":")
			dOldDigest[sKey]=sValue	
	else:
		print "no digest file"

	# new��old�Ա�
	lChange=[]
	lNew=[]
	for k,sNewDigest in dNewDigest.iteritems():
		sOldDigest=dOldDigest.get(k)
		replaceKey = k#.replace(sDir+"\\", "")

		if not sOldDigest:
			lNew.append(replaceKey)	
		elif sOldDigest!=sNewDigest:
			lChange.append(replaceKey)
			
	if lChange:
		print "[===change files num:%d===]"%(len(lChange))
		i=0
		for sFile in lChange:
			i+=1
			print "\t%d\t%s"%(i,sFile)
	if lNew:
		print "[===add files num:%d===]"%(len(lNew))
		i=0
		for sFile in lNew:
			i+=1
			print "\t%d\t%s"%(i,sFile)

	
	if lChange or lNew:
		# ���뵽Ŀ��Ŀ¼���
		os.chdir(gtDir)

		zf=zipfile.ZipFile(zipName,"w",compression=zipfile.ZIP_DEFLATED)
		for sFile in lChange+lNew:
			zf.write(sFile)
		zf.close()

		os.chdir("../../")

		# ������õ��ļ��Ƴ���
		sourceFile=gtDir+"\\"+zipName
		shutil.move(sourceFile,zipName)
		print "[===move file===]source:%s, target:%s"%(sourceFile,zipName)

		# ��¼���µ�MD5
		l=[]
		lKey=dNewDigest.keys()
		lKey.sort()
		for k in lKey:
			l.append(k+":"+dNewDigest[k])		
		f=open(gsPyDigest,'w')
		f.seek(0,0)
		f.write("\n".join(l))
		f.close()
		print "[===record md5===]file:%s"%(gsPyDigest)

	else:
		print "no change"

def clean():
	""" clean """
	print "[===clean===]"
	os.system("svn update")
	os.system("mvn clean package -Dmaven.test.skip=true")

	



if __name__ == "__main__":	
	
	# ����
	clean()
	# �ȸ���
	hotupdatePackage()

	# ����
	# fullPackage()
	# os.system("pause")

	print "end"
