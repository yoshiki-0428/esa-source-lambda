# esa-source-lambda

Esa.ioのWebhookを利用して特定GitHubリポジトリに自動コミットするLambdaファンクションです。

GatsbyなどのCMSにEsaの記事作成をトリガーにPushすることが可能です。

# 機能

- Esa.ioのWebHookをトリガーに指定したGitHubリポジトリに対しコミットを行う
- Esaのデータソースに対応
    - 特定のディレクトリ毎にWebHookルールが設定できるため、`Blog/Tech/`などのディレクトリの更新に対応可能
- WebHookイベント
    - post_create: YYYY-MM-DD--{esa_number}.md を作成
    - post_update: YYYY-MM-DD--{esa_number}.md を更新
    - post_archive: 未対応
    - post_delete: 未対応

# Architect

![](https://img.esa.io/uploads/production/attachments/15569/2020/06/11/82539/c66b1d15-c5ae-41f5-9e09-df46eee8febc.png)

# How to

## Lambda FWの serverless をインストール
```
npm install -g serverless
```

### 本リポジトリのLambda をインストール
```
serverless create -u https://github.com/yoshiki-0428/esa-source-lambda -n {your-name-func:tech-blog}
```

## 環境変数をセット

### AWS IAM Secret & Access Key

[設定方法はこちら](https://www.serverless.com/framework/docs/providers/aws/guide/credentials/)

```
export AWS_ACCESS_KEY_ID={your-aws-access-id}
export AWS_SECRET_ACCESS_KEY={your-aws-secret-access-key}
```

### GitHub AccessToken

[設定方法はこちら](https://help.github.com/ja/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)

> repoの実行権限があればOK

```
export GITHUB_TOKEN={your-github-token}
export GITHUB_REPOSITORY={your-owner-name}/{your-repository-name}
ex) yoshiki-0428/esa-source-lambda
```

コミット対象のブランチを指定
```
export BRANCH_NAME=heads/master
```

コミット対象のディレクトリを指定

> src/content の場合 content配下にmdファイルが保存されます

```
export COMMIT_DIR=src/content
```

Esa.ioのWebHookの際に認証するEsa-Signatureを設定（EsaのWebHook Generic側にも同じキーを設定する）

[詳細](https://docs.esa.io/posts/37#X-Esa-Signature)

![](https://img.esa.io/uploads/production/attachments/15569/2020/06/11/82539/2c32f3b6-ec46-4572-86f8-efd099a27ac4.png)

```
export ESA_SECRET_KEY=my_secret_key
```

ファンクション名を設定

> Lambda名が esa-source-lambda-test-blog になります 
```
export FUNC_NAME=test
```

## deploy

セットした環境変数をもとにAWS Lambdaへとdeployします

```
serverless deploy
```

```
...................................
Serverless: Stack update finished...
Service Information
service: esa-source-lambda
stage: dev
region: us-east-1
stack: esa-source-lambda-dev
resources: 10
api keys:
  None
endpoints:
  POST - https://{hoge}.execute-api.us-east-1.amazonaws.com/dev/
functions:
  main: esa-source-lambda-test-blog
layers:
  None
Serverless: Run the "serverless" command to setup monitoring, troubleshooting and testing.

```

AWSの画面を確認し設定されていることを確認してください

![](https://img.esa.io/uploads/production/attachments/15569/2020/06/11/82539/5218f758-35b5-4236-b235-414d332803ff.png)

## Esa Generic WebHookの設定

```
endpoints:
  POST - https://{hoge}.execute-api.us-east-1.amazonaws.com/dev/
```
先程取得したURLとEsa-Signatureを設定します

![](https://img.esa.io/uploads/production/attachments/15569/2020/06/11/82539/2c32f3b6-ec46-4572-86f8-efd099a27ac4.png)

## esa.ioでファイルを編集してみる

Webhookで指定したディレクトリのファイルをShip It!してみましょう。デフォルトでwipの場合は「何もしない」設定になっています。


# 最後に

もしよろしければこのリポジトリに `Star` をお願いしますmm 本人のやる気に繋がります。