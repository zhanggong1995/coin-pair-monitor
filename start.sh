#!/bin/bash
if [ $# != 1 ];then
  echo 请带上参数 star stop restart
fi
case $1 in
start)
    nohup python quote_depth.py 13.231.78.69 hb.btcusdt,hb.eosusdt,hb.ethusdt,ba.btcusdt,ba.eosusdt,ba.ethusdt,okex.btcusdt > /dev/null &
    nohup python quote_trade.py 13.231.78.69 hb.btcusdt,hb.eosusdt,hb.ethusdt,ba.btcusdt,ba.eosusdt,ba.ethusdt,okex.btcusdt > /dev/null &
  ;;
stop)
    Depth_pid=`ps -ef |grep "python quote_depth.py"|grep -v grep|awk '{print $2}'`
    Trade_pid=`ps -ef |grep "python quote_trade.py"|grep -v grep|awk '{print $2}'`
    kill -9 $Depth_pid
    kill -9 $Trade_pid
  ;;
restart)
    Depth_pid=`ps -ef |grep "python quote_depth.py"|grep -v grep|awk '{print $2}'`
    Trade_pid=`ps -ef |grep "python quote_trade.py"|grep -v grep|awk '{print $2}'`
    kill -9 $Depth_pid
    kill -9 $Trade_pid
    nohup python quote_depth.py 13.231.78.69 hb.btcusdt,hb.eosusdt,hb.ethusdt,ba.btcusdt,ba.eosusdt,ba.ethusdt,okex.btcusdt > /dev/null &
    nohup python quote_trade.py 13.231.78.69 hb.btcusdt,hb.eosusdt,hb.ethusdt,ba.btcusdt,ba.eosusdt,ba.ethusdt,okex.btcusdt > /dev/null &
  ;;
esac


