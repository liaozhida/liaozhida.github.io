# QA.md

### Only one AsyncAnnotationBeanPostProcessor may exist within the context

```
<task:annotation-driven executor="customAsyncTaskExecutor" scheduler="taskScheduler"/>

<task:annotation-driven/>
```

[ref](https://stackoverflow.com/questions/5440429/springs-scheduled-error-only-one-asyncannotationbeanpostprocessor-may-exist)

### Spring Data MongoDB error ，The matching wildcard is strict, but no declaration can be found for element 'mongo:mongo'.**

You are missing http://www.springframework.org/schema/data/mongo in your schemaLocation.

Minimal config for your beans should look like:

```
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:mongo="http://www.springframework.org/schema/data/mongo"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
        http://www.springframework.org/schema/beans/spring-beans.xsd
        http://www.springframework.org/schema/data/mongo
        http://www.springframework.org/schema/data/mongo/spring-mongo.xsd">

    <mongo:mongo host="localhost" port="27017" id="mongo"/>

    <bean id="mongoTemplate"
          class="org.springframework.data.mongodb.core.MongoTemplate">
        <constructor-arg name="mongo" ref="mongo"/>
        <constructor-arg name="databaseName" value="SADB"/>
    </bean>
</beans>

```
[https://stackoverflow.com/questions/33003357/spring-data-mongodb-error](https://stackoverflow.com/questions/33003357/spring-data-mongodb-error)