#-*-coding:utf-8-*-
import os
import md5
import time
import shutil
import zipfile

#######################################
# 作用：基本maven进行增量变动文件的打包
# 原理：用文件记录maven编译后的所有文件的md5，
#       每次更新对比上一次的md5，找到所有变化的文件
# 作者：victor zheng
#######################################


# 配置
#######################################
# 文件md5记录
gsPyDigest="md5Digest.txt"
# 项目名
serverName="video-server-1.17.2"
# 最终zip包名
zipName=time.strftime("videoserver_hotupdate_%Y%m%d_%H%M.zip",time.localtime())

#######################################


def loopDir(sDir,sNextDir = ""):
	""" 遍历目录 """

	# 字典存储md5信息|key:文件，value:文件对应的md5
	dDigest={}
	sCwd=os.getcwd() +"\\"+ sNextDir

	for sSub in os.listdir(sDir):		
		sNew=os.path.join(sDir,sSub)

		if os.path.isdir(sNew):
			# 遍历子目录			
			dDigest.update(loopDir(sNew,sNextDir))
		elif os.path.isfile(sNew):

			sKey=sNew.replace(sCwd+"\\","")
			# 二进制只读方式加载文件内容
			f=open(sNew,'rb')
			sText=f.read()
			f.close()
			obj=md5.new(sText)			
			dDigest[sKey]=obj.hexdigest()			
	return dDigest




def fullPackage():
	""" 整包 """
	targetDir = "target"
	sCwd=os.getcwd() + "\\" + targetDir
	print sCwd
	
	for sSub in os.listdir(targetDir):
		if sSub.endswith(".war"):
			fileName=sSub
			print sSub+"~~~~~~~~~~~~"

	#移包
	shutil.move("target/"+fileName,".")
	#重命名
	os.rename(fileName,"video-server.war")


def hotupdatePackage():
	""" 热更包 """

	gtDir = "target\\%s"%(serverName)
	print "compile the results directory:%s"%gtDir

	dNewDigest={}
	fullPath=os.getcwd()+"\\%s"%(gtDir)
	d=loopDir(fullPath, gtDir)
	dNewDigest.update(d)

	# 旧的文件的md5快照
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

	# new和old对比
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
		# 进入到目标目录打包
		os.chdir(gtDir)

		zf=zipfile.ZipFile(zipName,"w",compression=zipfile.ZIP_DEFLATED)
		for sFile in lChange+lNew:
			zf.write(sFile)
		zf.close()

		os.chdir("../../")

		# 将打包好的文件移出来
		sourceFile=gtDir+"\\"+zipName
		shutil.move(sourceFile,zipName)
		print "[===move file===]source:%s, target:%s"%(sourceFile,zipName)

		# 记录最新的MD5
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
	
	# 编译
	clean()
	# 热更包
	hotupdatePackage()

	# 整包
	# fullPackage()
	# os.system("pause")

	print "end"
