# Despliegue de un servidor web en AWS Elastic Beanstalk a través de CI/CD con GitHub Actions

En el presente repositorio se va mostrar cómo automatizar el despliegue de un servidor web hecho en python con el framework flask. Para lograr la automatización se va configurar un pipeline CI/CD con GitHub Actions lo que permite agilizar el proceso de desarrollo, pruebas y despliegue en AWS Elastic Beanstalk que es un servicio PaaS (Plataforma como servicio) que ofrece AWS.  

![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![AWS](https://img.shields.io/badge/Amazon_AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![GitHubActions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

<hr>

Se crea un servidor web sencillo en python utilizando el framework flask. Para el presente repositorio la aplicación web se llama **application.py**

Se crea un directorio llamando test y dentro un archivo llamado test_app.py. Este archivo va a ejecutar una prueba que consiste en verificar si una función de la aplicación web retorna exactamente **Hello World**

En el archivo requirements.txt se definen las librerias que utiliza la aplicación web y que se van a instalar en AWS Elastic Beanstalk. 

<hr>

Para crear el workflow en Github Actions se crea un directorio llamado **.github** y dentro se crea otro directorio llamado **workflows**

Dentro de **workflows** se crea un archivo con extensión .yml. Para el presente repositorio ese archivo se llama **python-app.yml**. En este archivo se define el flujo de trabajo para automatizar las tareas de desarrollo, pruebas y despliegue. 

En la primer parte con etiqueta **name** se define el nombre del workflow, la etiqueta **on** indica cómo se va a ejecutar el workflow, para este caso siempre que se realice un push o un pull request al repositorio se da inicio al workflow. En **permissions** se otorga permiso al workflow para acceda a los archivos del repositorio. 

            name: Python application

            on:
                push:
                    branches: [ "main" ]
                pull_request:
                    branches: [ "main" ]

            permissions:
                contents: read

En la segunda parte de define donde se va a ejecutar el workflow y sus diferentes etapas. En **jobs** se define un trabajo llamado **build** que se ejecutará en una máquina virtual basada en ubuntu. 

            jobs:
                build:
                    runs-on: ubuntu-latest
    

En los siguientes **steps** se define las diferentes etapas que hace parte del flujo de trabajo:

1. Clonar el repositorio en el runner (máquina virtual)

            - uses: actions/checkout@v3

2. Configurar Python 3.10 en el runner (máquina virtual)

            - name: Set up Python 3.10
            uses: actions/setup-python@v3
            with:
                python-version: "3.10"

3. Instalar dependencias y librerías que se encuentren en el archivo requirements.txt. Por fuera de requirements se instala pytest para realizar pruebas unitarias y flake8 para análisis de código. 

            - name: Install dependencies
              run: |
                python -m pip install --upgrade pip
                pip install flake8 pytest
                if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

4. Análisis de código con flake8 para detectar errores de sintaxis y problemas de estilo.
La primera línea detiene el flujo de trabajo si encuentra errores graves.
La segunda línea trata todos los errores como advertencias (no detiene el flujo) y aplica configuraciones específicas como la complejidad máxima del código (--max-complexity=10) y la longitud máxima de línea (--max-line-length=127).

            - name: Lint with flake8
            run: |
                flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

5. Ejecutar pruebas con pytest definidas en el archivo **test_app.py**

            - name: Test with pytest
            run: |
                export PYTHONPATH=.
                pytest

6. Se crear un .zip para comprimir la aplicación web y el archivo requirements.txt que posteriormente será almacenado en un bucket S3 desde donde el Elastic Beanstalk lo utilizará para hacer el despliegue de la aplicación web. 

            - name: Create package for deployment
            run: zip -r python_package.zip application.py requirements.txt


7. Configurar credenciales de AWS para realizar el despliegue en AWS Elastic Beanstalk. Por seguridad las credenciales se configuran en variables **secrets** del repositorio GitHub. 

            - name: Configure AWS credentials
            uses: aws-actions/configure-aws-credentials@v1
            with:
                aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
                aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
                aws-region: "us-east-1"

8. Subir el archivo .zip comprimido a un bucket de S3 denominado app-python-deploy

                - name: Upload the package to S3 Bucket
                run: aws s3 cp python_package.zip s3://app-python-deploy/


9. Instalar la CLI de Elastic Beanstalk para realizar la configuración desde la terminal de comandos

                - name: Install EB CLI
                run: |
                    python -m pip install --upgrade pip
                    pip install awsebcli


10. Crear una aplicación en Elastic Beanstalk llamada flask-python con Python 3.9. Y crear el entorno llamado flask-python-env

                - name: Create application in AWS EBS
                run: |
                    eb init -p python-3.9 flask-python --region us-east-1
                    eb create flask-python-env


11. Desplegar en Elastic Beanstalk si los demás pasos fueron exitosos. 


                - name: Deploy to AWS Elasticbeanstalk
                if: github.ref == 'refs/heads/main' && job.status == 'success'
                run: |
                    aws elasticbeanstalk create-application-version --application-name flask-python --source-bundle "S3Bucket=app-python-deploy,S3Key=python_package.zip" --version-label v1
                    aws elasticbeanstalk update-environment --environment-name flask-python-env --version-label v1

12. En el repositorio GitHub en la pestaña Actions se puede verificar el flujo de los **steps**

13. Si finalmente el flujo de trabajo realiza los steps de forma exitosa, se puede ir al servicio de AWS ELastic Beanstalk y verificar que se hizo el despliegue. Este servicio suministra un DNS a través del cual se puede acceder a la aplicación web. 