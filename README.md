# Apple Transporter IPA
让 Windows 和 Linux 开发者无需 Mac 设备即可轻松将 IPA 包上传到 TestFlight。


功能特点
 * 支持 Windows 和 Linux 系统
 * 无需 Mac 设备即可上传 IPA 到 TestFlight
 * 桌面化操作
 * 亦可命令行提交
 * 本机存储上传信息,只需要填写一次。

   
## 安装指南
本程序依托Apple官方程序
Windows和Linux都需要安装AppleTransporter

[Apple官方地址](https://help.apple.com/itc/transporteruserguide/)

[Windows下载](https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/ra/resources/download/public/Transporter__Windows/bin)

[Linux下载](https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/ra/resources/download/public/Transporter__Linux/bin)
  


## 程序说明
  ipa_uploader.py  主程序 GUI界面，已经联动AppStoreInfo.plist生成，一键上传，使用可看使用说明

  generate_appstoreinfo.py 为解析Ipa文件 生成AppStoreInfo.plist 供上传Apple使用。

  如果只需要AppStoreInfo.plist，可以使用以下命令：
  ```python
     python generate_appstoreinfo.py <IPA文件路径> <输出二进制plist路径>
   ```
  这个程序可以实现从 IPA 包中提取 info.plist，生成二进制版本的 AppStoreInfo.plist。程序的主要功能如下：
  
  功能说明
   * 自动从 IPA 包中提取 info.plist 文件
   * 解析 info.plist 获取三个关键信息：
     - 应用版本号（CFBundleShortVersionString）
     - 构建版本号（CFBundleVersion）
     - 包名（CFBundleIdentifier）
   * 生成最终的二进制版本 AppStoreInfo.plist

  去掉了AppStoreInfo.plist所有不需要的节点

  Mac生成AppStoreInfo.plist文件可以使用以下命令，不需要以上程序：

  ```
   xcrun swinfo -o AppStoreInfo.plist -prettyprint true --plistFormat binary -f xxx.ipa
  ```


  
## 使用说明

cd到程序目录，直接执行以下代码即可

   ```python
     python ipa_uploader.py
   ```

使用过后,会把输入信息存在同目录的json文件中，下次自动填充。
多个开发者主体使用TeamID分辨，下拉框选取。

特别注意：需要拥有开发者 "管理” 权限。


### 打开界面

<img width="652" height="562" alt="image" src="https://github.com/user-attachments/assets/d21dfb6a-1b5a-4d97-b0f6-89401f2fd2d7" />

### Team ID:

[Apple开发者后台](https://developer.apple.com/account) 往下滚动

<img width="821" height="608" alt="image" src="https://github.com/user-attachments/assets/d4f76f86-e615-4248-9356-ddb4db844a08" />

### App 专用密码：

[Apple账号设定](https://account.apple.com/account/manage)  密码只显示一次，注意复制并保存，可删除重新生成。
<img width="842" height="687" alt="image" src="https://github.com/user-attachments/assets/deb92152-7d10-45d7-8241-3efff54cdad7" />


## 许可证
   


