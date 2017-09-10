# gitlab打标签推送镜像.md

```
    - docker build -t docker.umiit.cn:5043/v3/y-app:$CI_BUILD_TAG .
    - docker push docker.umiit.cn:5043/v3/y-app:$CI_BUILD_TAG
    - docker tag -f docker.umiit.cn:5043/v3/y-app:$CI_BUILD_TAG docker.umiit.cn:5043/v3/y-app:latest
    - docker push docker.umiit.cn:5043/v3/y-app:latest
```