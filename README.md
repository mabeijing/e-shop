学习指南

Flask核心点

1，wsgi协议

2，2个本地栈。LocalStack ==> _request_ctx_stack, _app_ctx_stack

3，2个上下文。AppContext, RequestContext

4，4个代理对象。current_app, g, request, session

5，Jinja2模板


Flask重要概念：
*   Flask是符合wsgi协议的应用，即wsgi服务器收到请求后，会执行应用app(environ, tart_response)。也就是说Flask必须实现__call__， 
    environ是wsgi服务器传递过来包含所有请求参数的一个字典，tart_response是wsgi接收的回调函数。都是固定参数。
    
*   flask执行call方法后，会ctx = self.request_context(environ)创建一个请求上下文，ctx.push()。
    先给request赋值
    然后将应用上下文入栈。app_ctx = self.app.app_context()创建一个应用上下文，app_ctx.push()入栈。
    最后给session赋值

*   在RequestContext和AppContext都入栈后，代理对象就可以访问了。 
    request代理，其实就是RequestContext.request。必须拿到请求environ才有值。
    session代理，其实就是RequestContext.session。值保存在浏览器或者redis，所以可以跨请求获取。
    current_app就是栈顶flask的实例对象。
    g是应用上下文的一个属性读取器。每次请求都不一样。生命周期一次请求。
    作用域都是当前请求线程内。无法跨线程访问。生命周期是请求入栈到出栈。
    

代理对象必须在入栈后才能使用
应用上下文可以通过flask实例app.app_context()创建一个应用上下文。获取代码逻辑，自己的代码都可以在应用上下文种执行。
请求上下文比较难构造。app.app.test_request_context()必须传入值才能得到有效上下文。



启动celery
启动celery worker： celery -A app.celery_app worker -P solo --loglevel=info
启动celery定时任务： celery -A app.celery_app beat
