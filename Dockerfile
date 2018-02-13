FROM	php:5.6.24-cli

ENV		PATH_CODE_SNIFFER /bin/codesniffer

RUN		mkdir $PATH_CODE_SNIFFER && \
		apt-get update && \
		apt-get install -y git npm python-setuptools cowsay && \
		apt-get clean && \
		docker-php-ext-install zip && \
		ln -s /usr/local/bin/php /usr/bin/ && \
		ln -s /usr/bin/nodejs /usr/bin/node && \
		easy_install pip

COPY	./ $PATH_CODE_SNIFFER

RUN		useradd --create-home --no-log-init anyuan && \ 
		chown anyuan:anyuan -R $PATH_CODE_SNIFFER && \
		cd $PATH_CODE_SNIFFER && \
		npm install && \
		pip install -r requirements.txt	

USER    anyuan

RUN		cd $PATH_CODE_SNIFFER && \
		./bin/composer.phar install

WORKDIR /code

#Build
#sudo docker build -t git_code_sniffer_hook:180213  ./
