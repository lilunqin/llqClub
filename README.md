# bbs
# 论坛项目
个人项目部署地址：http://lilunqin.club/ （已停止维护）

# 主要功能
- 基于MVC原则实现
- 帖子和评论的添加、修改、删除，实现权限控制
- 用户信息修改
- 上传头像
  - 过滤用户输入
- 站内信/邮件
  1. 站内信/私信
  2. at
  3. 通知
  4. 发邮件 marrow.mailer
  5. 重置密码
- 安全相关
  - 防SQL注入
  - 实现对CSRF、XSS攻击的防范
  - 用户密码加盐

# 如何运行本项目
  需自行上传config.py和secret.py
  ```python
  config.py
  admin_mail = '' # 用来实现“通知”功能的邮件账号，用的是腾讯企业邮箱
  test_mail = ''  # 收邮件的测试账号
  ```

  ```python
  secret.py
  secret_key = '' # 密码加盐字符
  database_password ='' # 数据库密码
  mail_password ='' # 用来实现“通知”功能的邮件账号的邮箱密码
  ```
  运行环境python3.6，
  运行flask_dev.py
