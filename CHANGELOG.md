# CHANGELOG

## v2

### k8s_deploy.yml

#### Breaking Changes

The default authentication flow to the azure clusters in the workflow was changed from service principal to oidc flow.
Service principal authenctication is still supported, but not by default:

- Clusters with OIDC Flow:
    - Adapt your GitHub actions for deployments:
        ```diff
        Index: .github/workflows/deploy_*.yml
                secrets:
            -       az_service_principal: secret-service-principal
            +       az_client_id: secret-client-id
            +       az_tenant_id: secret-tenant-id
            +       az_subscription_id: secret-subscription-id
            ```
    - Execute the following for your repo with the token having the `repo` permissions set:
        ```shell
        curl -vvvv -L \
        -X PUT \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer <TOKEN>"\
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/repos/UbiqueInnovation/{REPO}/actions/oidc/customization/sub \
        -d '{"use_default":false}'
        ```
- Clusters that remain at service principal authentication:
    ```diff
    Index: .github/workflows/deploy_*.yml
        with:
    +       az_login_flow: service_principal
    ```
## v1

### mvn_docker_image.yml

#### Breaking Changes

Previously, jib-maven-plugin was not defined inside the project poms, yet now it is. All projects need to have their
usages of mvn_docker_image.yml@main updated to mvn_docker_image.yml@v1 or do the following changes in their poms:

- Parent `pom.xml`:
```xml
<build>
    <pluginManagement>
        <plugins>
            <plugin>
                <groupId>com.google.cloud.tools</groupId>
                <artifactId>jib-maven-plugin</artifactId>
                <version>3.3.2</version>

                <dependencies>
                    <dependency>
                        <!-- This ensures spring-boot-devtools are not included
                        in the WAR build like the spring-boot-maven-plugin also
                        ensures it does not exist in the JAR builds -->
                        <groupId>com.google.cloud.tools</groupId>
                        <artifactId>jib-spring-boot-extension-maven</artifactId>
                        <version>0.1.0</version>
                    </dependency>
                </dependencies>

                <configuration>
                    <pluginExtensions>
                        <pluginExtension>
                            <implementation>
                                com.google.cloud.tools.jib.maven.extension.springboot.JibSpringBootExtension
                            </implementation>
                        </pluginExtension>
                    </pluginExtensions>
                </configuration>
            </plugin>
        </plugins>
    </pluginManagement>
</build>
```

- `pom.xml` of a WS without job module:
```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
        <plugin>
            <groupId>com.google.cloud.tools</groupId>
            <artifactId>jib-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

- `pom.xml` of a WS with job module:
```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <executions>
                <execution>
                    <id>build-info</id>
                    <goals>
                        <goal>build-info</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
        <plugin>
            <groupId>com.google.cloud.tools</groupId>
            <artifactId>jib-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```