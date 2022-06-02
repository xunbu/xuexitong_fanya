from threading import Thread,RLock


_messagelock=RLock()#用来传递选课的网站
_message=None#记录选择的index（章节在网页中的index）

_urllock=RLock()#用来传递课程地址
_lessonurl=None

globaldict={'messagelock':_messagelock,'message':_message,'urllock':_urllock,'lessonurl':_lessonurl}