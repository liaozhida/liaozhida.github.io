# 定时任务Cron表达式.md


```
Expression	Means
0 0 12 * * ?				Fire at 12:00 PM (noon) every day
0 15 10 ? * *				Fire at 10:15 AM every day
0 15 10 * * ?				Fire at 10:15 AM every day
0 15 10 * * ? *				Fire at 10:15 AM every day
0 15 10 * * ? 2005			Fire at 10:15 AM every day during the year 2005
0 * 14 * * ?				Fire every minute starting at 2:00 PM and ending at 2:59 PM, every day
0 0/5 14 * * ?				Fire every 5 minutes starting at 2:00 PM and ending at 2:55 PM, every day
0 0/5 14,18 * * ?			Fire every 5 minutes starting at 2:00 PM and ending at 2:55 PM, AND fire every 5 minutes starting at 6:00 PM and ending at 6:55 PM, every day
0 0-5 14 * * ?				Fire every minute starting at 2:00 PM and ending at 2:05 PM, every day
0 10,44 14 ? 3 WED			Fire at 2:10 PM and at 2:44 PM every Wednesday in the month of March
0 15 10 ? * MON-FRI			Fire at 10:15 AM every Monday, Tuesday, Wednesday, Thursday and Friday
0 15 10 15 * ?				Fire at 10:15 AM on the 15th day of every month
0 15 10 L * ?				Fire at 10:15 AM on the last day of every month
0 15 10 ? * 6L				Fire at 10:15 AM on the last Friday of every month
0 15 10 ? * 6L				Fire at 10:15 AM on the last Friday of every month
0 15 10 ? * 6L 2002-2005	Fire at 10:15 AM on every last friday of every month during the years 2002, 2003, 2004, and 2005
0 15 10 ? * 6#3				Fire at 10:15 AM on the third Friday of every month
0 0 12 1/5 * ?				Fire at 12 PM (noon) every 5 days every month, starting on the first day of the month
0 11 11 11 11 ?				Fire every November 11 at 11:11 AM
 
```

```
**Expression**					**Meaning**
0 0 12 * * ?					Fire at 12pm (noon) every day
0 15 10 ? * *					Fire at 10:15am every day
0 15 10 * * ?					Fire at 10:15am every day
0 15 10 * * ? *					Fire at 10:15am every day
0 15 10 * * ? 2005				Fire at 10:15am every day during the year 2005
0 * 14 * * ?					Fire every minute starting at 2pm and ending at 2:59pm, every day
0 0/5 14 * * ?					Fire every 5 minutes starting at 2pm and ending at 2:55pm, every day
0 0/5 14,18 * * ?				Fire every 5 minutes starting at 2pm and ending at 2:55pm, AND fire every 5 minutes starting at 6pm and ending at 6:55pm, every day
0 0-5 14 * * ?					Fire every minute starting at 2pm and ending at 2:05pm, every day
0 10,44 14 ? 3 WED				Fire at 2:10pm and at 2:44pm every Wednesday in the month of March.
0 15 10 ? * MON-FRI				Fire at 10:15am every Monday, Tuesday, Wednesday, Thursday and Friday
0 15 10 15 * ?					Fire at 10:15am on the 15th day of every month
0 15 10 L * ?					Fire at 10:15am on the last day of every month
0 15 10 L-2 * ?					Fire at 10:15am on the 2nd-to-last last day of every month
0 15 10 ? * 6L					Fire at 10:15am on the last Friday of every month
0 15 10 ? * 6L					Fire at 10:15am on the last Friday of every month
0 15 10 ? * 6L 2002-2005		Fire at 10:15am on every last friday of every month during the years 2002, 2003, 2004 and 2005
0 15 10 ? * 6#3					Fire at 10:15am on the third Friday of every month
0 0 12 1/5 * ?					Fire at 12pm (noon) every 5 days every month, starting on the first day of the month.
0 11 11 11 11 ?					Fire every November 11th at 11:11am.
```

[A Cron Expressions](https://docs.oracle.com/cd/E12058_01/doc/doc.1014/e12030/cron_expressions.htm)
[ 详细！ CronTrigger Tutorial](http://www.quartz-scheduler.org/documentation/quartz-2.x/tutorials/crontrigger.html)
[每天一个linux命令（50）：crontab命令](http://www.cnblogs.com/peida/archive/2013/01/08/2850483.html)