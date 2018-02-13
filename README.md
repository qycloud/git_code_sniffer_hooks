## 安装：

### 代码：
```shell
mkdir ~/bin/
cd ~/bin/
git clone https://github.com/qycloud/git_code_sniffer_hooks.git
```

### Docker版快速安装：
```shell
mkdir ~/bin/
cd ~/bin/
git clone https://github.com/qycloud/git_code_sniffer_hooks.git

#此处假设您的项目目录为~/workspace/test
ln -s ~/bin/git_code_sniffer_hooks/pre-commit-docker ~/workspace/test/.git/hooks/pre-commit
```
enjoy! P

### 原生安装
#### PHP相关依赖：

```shell
curl -s https://getcomposer.org/installer | php -- --install-dir=$HOME/bin
chmod +x ~/bin/composer.phar
cd ~/bin/git_code_sniffer_hooks/
~/bin/composer.phar install
```

#### NodeJs相关依赖：

```shell
sudo add-apt-repository ppa:chris-lea/node.js
sudo apt-get update
sudo apt-get install nodejs
cd ~/bin/git_code_sniffer_hooks/
npm install
```

#### Python相关依赖：

```shell
sudo apt-get install python-setuptools
sudo easy_install pip
sudo pip install -r ~/bin/git_code_sniffer_hooks/requirements.txt
```

#### 其它：

```shell
sudo apt-get install cowsay
```

## 配置：

```shell
#此处假设您的项目目录为~/workspace/test
ln -s ~/bin/git_code_sniffer_hooks/pre-commit ~/workspace/test/.git/hooks/
ln -s ~/bin/git_code_sniffer_hooks/pre-receive ~/workspace/test/.git/hooks/
```

## 手动检测：

```shell
~/bin/git_code_sniffer_hooks/bin/phpcs ~/demo.php # PHP
~/bin/git_code_sniffer_hooks/bin/jshint ~/demo.js # JavaScript
```
