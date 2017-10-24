No packages available for installation.md

###### 方法1 
I had the same issue following an upgrade, but saw this in the readme and ran this python script which fixed it for me (ctrl + ' to bring up the console then ran the following command)


###### 方法2

```
import urllib.request,os,sys; exec("if sys.version_info < (3,) or os.name != 'nt': raise OSError('This code is for Windows ST3 only!')"); pr='Preferences.sublime-settings'; ip='ignored_packages'; n='Package Control'; s=sublime.load_settings(pr); ig=s.get(ip); ig.append(n); s.set(ip,ig); sublime.save_settings('Preferences.sublime-settings'); pf=n+'.sublime-package'; urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler())); by=urllib.request.urlopen('https://packagecontrol.io/'+pf.replace(' ','%20')).read(); open(os.path.join(sublime.installed_packages_path(),pf),'wb').write(by); ig.remove(n); s.set(ip,ig); sublime.save_settings(pr); print('Package Control: 3.0.0 upgrade successful!')

```