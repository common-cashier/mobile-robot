GATEWAY=`ps -ef|grep gateway.py|grep -v grep|awk '{print $2}'`
for pid in $GATEWAY
do
  kill -9 $pid
done

#WEBSOCK=`ps -ef|grep websock.py|grep -v grep|awk '{print $2}'`
#for pid in $WEBSOCK
#do
#  kill -9 $pid
#done
#
#ROOT_SERVICE=`ps -ef|grep root_service.py|grep -v grep|awk '{print $2}'`
#for pid in $ROOT_SERVICE
#do
#  kill -9 $pid
#done      ，