# GitHub Actions, Dependencies, S3 and Lambda <br>

GitHub Actions is growing in popularity while Jenkins may still keep the momentum where few years ago Jenkins was dominating. Herewith is the 2023 survey about some major CI tools on the market.

![](/images/02-image01.png)
  Figure 1: 2023 survey on Popular CI tools https://blog.jetbrains.com/teamcity/2023/07/best-ci-tools/
<br><br>

And herewith is another view to compare both tools in term of CI/CD.

| Criteria               | GitHub Actions                                                                                              | Jenkins                                                                                        |
|------------------------|-------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| Hosting                | GitHub Actions is hosted on GitHub's infrastructure.                                                        | Jenkins needs to be self-hosted or hosted on a server.                                         |
| Integration            | GitHub Actions is tightly integrated with GitHub repositories.                                              | Jenkins can integrate with various source control systems.                                     |
| Configuration          | GitHub Actions uses YAML files for configuration.                                                           | Jenkins uses a web-based interface for configuration.                                          |
| Scalability            | GitHub Actions can scale automatically based on the workload.                                               | Jenkins requires manual configuration for scaling.                                             |
| Community              | GitHub Actions has a growing community and marketplace for actions.                                         | Jenkins has a large and established community with a wide range of plugins.                    |
| Pricing                | GitHub Actions offers free usage for public repositories and has a pricing model for private repositories.  | Jenkins is open-source and free to use.                                                        |
| Ease of Use            | GitHub Actions has a simpler setup and configuration process.                                               | Jenkins has a steeper learning curve and requires more manual configuration.                   |
| Ecosystem              | GitHub Actions has a growing ecosystem of pre-built actions.                                                | Jenkins has a vast ecosystem of plugins for various integrations and functionalities.          |
| Security               | GitHub Actions has built-in security features and permissions management.                                   | Jenkins requires manual configuration for security measures.                                   |
| Continuous Integration | GitHub Actions provides built-in CI/CD capabilities.                                                        | Jenkins is primarily a CI/CD tool but requires additional plugins for certain functionalities. |
| Distribution Method    | no installation needed as it is a Software as a Service, we still can use cli but everything happens online | Mainly through Jar file distribution                                                           |

We will cover few topics of GitHub Actions in correlation with its unique feature called dependencies as well as how it will interact with AWS for uploading file to S3 storage and calling a serverless Lambda function for example.

## THE BASIC <br>
Let's start with this simple code that we can run in GitHub Action for now.

```yaml
on: 
  push:
    branches:
      - main

jobs:
  build1:
    runs-on: ubuntu-latest
    steps: 
      - name: Check out code
        uses: actions/checkout@v2
      - name: Set up Python on our runner
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
            cd function
            python -m pip install --upgrade pip
            if  [ -f requirements.txt ]; then pip install -r requirements.txt -t .; fi
      - name: Create zip bundle
        run: |
            cd function
            zip -r ../${{github.sha}}.zip .
      - name: Archive Artifacts
        uses: actions/upload-artifact@v2
        with:
          name: zipped-bundle
          path: ${{github.sha }}.zip
```

This simple one job pipeline should be very straight forward and should give a successful build like below.

![](/images/02-image02.png)
Figure 2: Typical GitHub Action Job Steps
<br><br>

You may see couple uses inside the jobs steps such as actions/setup-python@v2 and actions/upload-artifact@v2. They are mainly some kind of Plugins as we know in Jenkins. Herewith are the comparison of the two.

![](/images/02-image03.png)
Figure 3: GitHub Action Marktetplace for uses:
<br><br>

As GitHub Actions was born just before the pandemic started we could see GitHub Actions marketplace now has quadruple the size of Jenkins Plugin

Criteria                               | Jenkins Plugin | GitHub Action Marketplace
---------------------------------------| ---------------| -------------------------
Integration with CI/CD                 | Yes            | Yes
Number of available plugins/actions    | 1500+          | 6000+
Ease of installation                   | Easy           | Easy
Community support                      | Active         | Active
Customizability                        | High           | High
Compatibility with different languages | Yes            | Yes
Integration with other tools           | Yes            | Yes
Ease of use for beginners              | Moderate       | Easy
Security features                      | Yes            | Yes
Pricing                                | Free           | Paid and Free
First release                          | 2011           | November 2019.

Another job that we can introduce in this quick demo would be as follow.

```yaml
publish1:
      runs-on: ubuntu-latest
      steps:
        - name: create release
          uses: actions/create-release@v1
          env:
            GITHUB_TOKEN: ${{ secrets.github_token }}
          with:
            tag_name: ${{ github.run_number }}
            release_name: Release from ${{ github.run_number }}
            body: New release for ${{ github.sha }}
            draft: false
            prerelease: false
```
This job would create some kind of zip files from the entire GitHub Action related projects, such as pipeline yml file, lambda function python file although in practical way when Lambda function needed to build from scratch from cli command this python file is ideally located in S3.
Now, imagine we have complex network of pipeline with one job has to complete before the other can start. Of course those two jobs above are not the perfect examples but we will use them anyway to demonstrate GitHub Pipeline dependencies (Needs) below.

## DEPENDENCIES
At the end of this exercise we will try to build below pipeline where we will re-use the two jobs above again and again for simplicity. Take a look at build3 jobs below.

![](/images/02-image04.png)
Figure 4: Example of GitHub Action Parallel Workflow and Dependencies
<br><br>

Herewith re-usable jobs from above codes. Let's focus on the dependencies.

```yaml
on: 
  push:
    branches:
      - main

jobs:
  build1:
    runs-on: ubuntu-latest
    steps: 
      - name: Check out code
        uses: actions/checkout@v2
      - name: Set up Python on our runner
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
            cd function
            python -m pip install --upgrade pip
            if  [ -f requirements.txt ]; then pip install -r requirements.txt -t .; fi
      - name: Create zip bundle
        run: |
            cd function
            zip -r ../${{github.sha}}.zip .
      - name: Archive Artifacts
        uses: actions/upload-artifact@v2
        with:
          name: zipped-bundle
          path: ${{github.sha }}.zip

  build2:
      runs-on: ubuntu-latest
      needs: [build1]
      steps: 
        - name: Check out code
          uses: actions/checkout@v2
        - name: Set up Python on our runner
          uses: actions/setup-python@v2
          with:
            python-version: 3.8
        - name: Install dependencies
          run: |
              cd function
              python -m pip install --upgrade pip
              if  [ -f requirements.txt ]; then pip install -r requirements.txt -t .; fi
        - name: Create zip bundle
          run: |
              cd function
              zip -r ../${{github.sha}}.zip .
        - name: Archive Artifacts
          uses: actions/upload-artifact@v2
          with:
            name: zipped-bundle
            path: ${{github.sha }}.zip

  build4:
        runs-on: ubuntu-latest
        needs: [build2]
        steps: 
          - name: Check out code
            uses: actions/checkout@v2
          - name: Set up Python on our runner
            uses: actions/setup-python@v2
            with:
              python-version: 3.8
          - name: Install dependencies
            run: |
                cd function
                python -m pip install --upgrade pip
                if  [ -f requirements.txt ]; then pip install -r requirements.txt -t .; fi
          - name: Create zip bundle
            run: |
                cd function
                zip -r ../${{github.sha}}.zip .
          - name: Archive Artifacts
            uses: actions/upload-artifact@v2
            with:
              name: zipped-bundle
              path: ${{github.sha }}.zip

  build5:
        runs-on: ubuntu-latest
        needs: [build2]
        steps: 
          - name: Check out code
            uses: actions/checkout@v2
          - name: Set up Python on our runner
            uses: actions/setup-python@v2
            with:
              python-version: 3.8
          - name: Install dependencies
            run: |
                cd function
                python -m pip install --upgrade pip
                if  [ -f requirements.txt ]; then pip install -r requirements.txt -t .; fi
          - name: Create zip bundle
            run: |
                cd function
                zip -r ../${{github.sha}}.zip .
          - name: Archive Artifacts
            uses: actions/upload-artifact@v2
            with:
              name: zipped-bundle
              path: ${{github.sha }}.zip

  publish1:
      runs-on: ubuntu-latest
      needs: build1    
      steps:
        - name: create release
          uses: actions/create-release@v1
          env:
            GITHUB_TOKEN: ${{ secrets.github_token }}
          with:
            tag_name: ${{ github.run_number }}
            release_name: Release from ${{ github.run_number }}
            body: New release for ${{ github.sha }}
            draft: false
            prerelease: false

  build3:
    runs-on: ubuntu-latest
    needs: [build4, build5]
    steps: 
      - name: Check out code
        uses: actions/checkout@v2
      - name: Set up Python on our runner
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
            cd function
            python -m pip install --upgrade pip
            if  [ -f requirements.txt ]; then pip install -r requirements.txt -t .; fi
      - name: Create zip bundle
        run: |
            cd function
            zip -r ../${{github.sha}}.zip .
      - name: Archive Artifacts
        uses: actions/upload-artifact@v2
        with:
          name: zipped-bundle
          path: ${{github.sha }}.zip

  build6:
    runs-on: ubuntu-latest
    needs: [build3, publish1]
    steps: 
      - name: Check out code
        uses: actions/checkout@v2
      - name: Set up Python on our runner
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
            cd function
            python -m pip install --upgrade pip
            if  [ -f requirements.txt ]; then pip install -r requirements.txt -t .; fi
      - name: Create zip bundle
        run: |
            cd function
            zip -r ../${{github.sha}}.zip .
      - name: Archive Artifacts
        uses: actions/upload-artifact@v2
        with:
          name: zipped-bundle
          path: ${{github.sha }}.zip
```

In some cases the line of the workflow could be overlapping, which is not the case here. If that happens, please just hover your mouse over the line.

![](/images/02-image05.png)
Figure 5: Example of hovering the mouse over the pipeline in case the workflow line is overlapping
<br><br>

We can can see here the Needs clauses are the ones building dependencies

```yaml
jobs:
  build1:
    ...

  build2:
    needs: [build1]
    ...

  build4:
    needs: [build2]
    ...
  
  build5:
    needs: [build2]
    ...

  publish1:
    needs: build1    
    ...
  
  build3:
    needs: [build4, build5]
    ...

  build6:
    needs: [build3, publish1]
    ...
```

In GitHub Actions the pipeline workflow is an integral part of CI/CD where in Jenkins this feature is normally available through plugins. Lots of them.

## S3 BUCKET

Now, let's try to connect GitHub and AWS account through aws cli command such as aws s3 cp command below. For sure we need to establish the connection securely and stored the credential of AWS_ACCESS_KEY and AWS_SECRET_KEY safely in Settings → Secrets and Variables → Actions

![](/images/02-image06.png)
Figure 6: Example of Secret setting in GitHub. Only the user who own this repo can see this.
<br><br>

```yaml
on: 
  push:
    branches:
      - main

jobs:

  build:
      runs-on: ubuntu-latest
      steps: 
        - name: Check out code
          uses: actions/checkout@v2
        - name: Set up Python on our runner
          uses: actions/setup-python@v2
          with:
            python-version: 3.8
        - name: Install dependencies
          run: |
              cd function
              python -m pip install --upgrade pip
              if  [ -f requirements.txt ]; then pip install -r requirements.txt -t .; fi
        - name: Create zip bundle
          run: |
              cd function
              zip -r ../${{github.sha}}.zip .
        - name: Archive Artifacts
          uses: actions/upload-artifact@v2
          with:
            name: zipped-bundle
            path: ${{github.sha }}.zip
            
  # upload:
  #   runs-on: ubuntu-latest
  #   needs: build
  #   steps:
  #     - name: Download artifact
  #       uses: actions/download-artifact@v2
  #       with:
  #         name: zipped-bundle
  #     - name: Configure AWS credentials
  #       uses: aws-actions/configure-aws-credentials@v1
  #       with:
  #         aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY }}
  #         aws-secret-access-key: ${{ secrets.AWS_SECRET_KEY }}
  #         aws-region: us-east-1
  #     - name: Upload to S3
  #       run: aws s3 cp 01-image01.png s3://sqlzoo/

  copy-to-s3:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Install AWS CLI
        run: |
          sudo apt-get install -y python3-pip
          pip3 install awscli --upgrade --user
      - name: Copy file to S3
        run: |
          aws configure set aws_access_key_id ${{ secrets.AWS_ACCESS_KEY }} && \
          aws configure set aws_secret_access_key ${{ secrets.AWS_SECRET_KEY }} && \
          aws configure set region us-east-1 && \
          aws configure set output json && \
          aws s3 cp 01-image01.png s3://sqlzoo/
```

As soon as we have all the credential and having an existing S3 folders (in this case I use sqlzoo) we can upload a file from our local to S3. Please note that this technique is widely used for local to S3, not quite for web to S3. You may need to curl that web file locally and uploaded separately after.

![](/images/02-image07.png)
Figure 7: Quick revisit, another example of GitHub Dependencies Example without and with needs clause.
<br><br>

In term of dependencies, we normally should let the build happen first before the copy-to-s3 unless this job does not have necessary engine to run. Why the first scenario above work, because build job complete fast and it a while for copy-to-s3 to start before reaching aws s3 cp command.

## LAMBDA FUNCTION

![](/images/02-image08.jpg)
Figure 8: Illustration of how a function works. It is called Lambda in AWS. In Azure it is called Functions.
<br><br>


In the last part of this GitHub Action discussion, I would like to bring one more thing also from AWS by calling Lambda function below (assuming it was already set before from AWS Console) and return back the function value as input parameters were given.

Herewith is a simple lambda function I saved inside lambda_function.py This code basically does not need any requirements.txt to install special package as import json is generally available from Python basic install.

```py
import json

def lambda_handler(event, context):
    x = event['X']
    y = event['Y']
    z = event['Z']
    
    if x == 0 or y == 0 or z == 0:
        return {
            'statusCode': 200,
            'body': json.dumps('One of the variables is zero')
        }
    else:
        result = x * y * z
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
```

The function above will take three input parameters, X, Y and Z. If any of them have a zero value some kind of message will appear otherwise the function will multiply the three values. Herewith is few examples.

![](/images/02-image09.png)
Figure 9: Example of two scenarios sending input parameter to Lambda and getting back the Responses
<br><br>

For some reason when I run the aws lambda invoke from Ubuntu 23.04 I have to add - -cli-binary-format raw-in-base64-out like below

```sh
aws lambda invoke --function-name my-func-2 --cli-binary-format raw-in-base64-out --payload '{"X": -1, "Y": 0, "Z": -1}' out && cat out
```

unless it would give

```sh
Invalid base64: "{"X": -1, "Y": 0, "Z": -1}"
```

In GitHub workflow file that additional parameter is going to cause error.

```yaml
on: 
  push:
    branches:
      - main

jobs:

  build:
      runs-on: ubuntu-latest
      steps: 
        - name: Check out code
          uses: actions/checkout@v2
        - name: Set up Python on our runner
          uses: actions/setup-python@v2
          with:
            python-version: 3.8
        - name: Install dependencies
          run: |
              cd function
              python -m pip install --upgrade pip
              if  [ -f requirements.txt ]; then pip install -r requirements.txt -t .; fi
        - name: Create zip bundle
          run: |
              cd function
              zip -r ../${{github.sha}}.zip .
        - name: Archive Artifacts
          uses: actions/upload-artifact@v2
          with:
            name: zipped-bundle
            path: ${{github.sha }}.zip
            
  lambda1:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Install AWS CLI
        run: |
          sudo apt-get install -y python3-pip
          pip3 install awscli --upgrade --user
      - name: Lambda
        run: |
          aws configure set aws_access_key_id ${{ secrets.AWS_ACCESS_KEY }} && \
          aws configure set aws_secret_access_key ${{ secrets.AWS_SECRET_KEY }} && \
          aws configure set region us-east-1 && \
          aws configure set output json && \
          aws lambda invoke --function-name my-func-2 --payload '{"X": -1, "Y": 2, "Z": -1}' out && cat out
  lambda2:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Install AWS CLI
        run: |
          sudo apt-get install -y python3-pip
          pip3 install awscli --upgrade --user
      - name: Lambda
        run: |
          aws configure set aws_access_key_id ${{ secrets.AWS_ACCESS_KEY }} && \
          aws configure set aws_secret_access_key ${{ secrets.AWS_SECRET_KEY }} && \
          aws configure set region us-east-1 && \
          aws configure set output json && \
          aws lambda invoke --function-name my-func-2 --payload '{"X": -1, "Y": 0, "Z": -1}' out && cat out
```

This lambda exercise assumes that we already have an existing lambda function named my-func-2 as below. If you don't have it yet just make a new one. It needs to know three things. In this case we will send the input X, Y and Z with cli commands not with AWS console like shown below.

```sh
1. The lambda function name
2. The runtime : choose Python 3.8
3. Create new role / Use existing role
```

![](/images/02-image10.png)
Figure 10: Simple Lambda to return multiplication of input X, Y and Z or a message if one of them is zero
<br><br>

![](/images/02-image11.png)
Figure 11: When reuse existing role, you don't need to delete newly created role  when you delete this function
<br><br>

![](/images/02-image12.png)
Figure 12: Example of entering input parameter through AWS Console, which is not the case here (we use cli)
<br><br>

## SUMMARY
GitHub Actions which allows building continuous integration and continuous deployment pipelines for testing, releasing and deploying software without the use of third-party websites/platforms. Some of good thought from GitHub Action as mentioned in https://resources.github.com/downloads/What-is-GitHub.Actions_.Benefits-and-examples.pdf would be

```txt
● Build, test, and deploy within the GitHub flow: Continuous
  Integration (CI) and continuous deployment (CD) (aka CI/CD)
  automations are typically the easiest way for someone to understand
  the full functionality of GitHub Actions. From automating tests to
  deploying code, Actions enables you to run CI/CD workflows in
  containers and virtual machines directly from your repository. You
  can also integrate your preferred tools third-party CI/CD tools directly
  into your repositories with Actions.

● Automate repetitive tasks: GitHub Actions can be used to
  automate an almost endless number of steps in the software
  development lifecycle. Whether it's the creation of a pull request, a
  new contributor joining your repository, a pull request being merged,
  or a web hook from a third-party application that is integrated with a
  given repository, you can introduce an automated response including
  sorting an issue, or assigning a reviewer to a pull request.

● Manage users easily at scale: Maintainers often use GitHub
  Actions to set organization rules including assigning developer
  permissions, notifying reviewers of new pull requests, and more. This
  makes it easier to manage a repository and all of the contributors in
  a given project.

● Easily add preferred tools and services to your project: From
  testing tools to CI/CD platforms, container management platforms to
  issue tracking platforms and chat applications, GitHub Actions gives
  you the ability to connect and integrate your preferred third-party
  tools and services directly into your repository. This is designed to
  make it simpler to manage typical workflows and build, test, and
  deploy code all within the GitHub flow.

● Quickly review & test code on GitHub: GitHub Actions lets you
  integrate any number of third-party testing tools directly into your
  workflow in your repo-at any step. Moreover, GitHub Actions
  enables multi-container testing and "matrix builds," which lets you
  run multiple tests on Linux, Windows, and macOS at the same time.

● Keep track of your projects: You can use GitHub Actions to
  monitor application builds, measure performance, track errors and
  more via integrations with third-party tools. GitHub Actions also
  produces live logs, which lets you watch your workflows run in real
  time. Live logs also give you the ability to copy a link from a failed
  step to identify and solve potential issues (they support color and
  emojis, too).
```
