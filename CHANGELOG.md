# CHANGELOG

## Latest

### mvn_docker_image.yml pre v1 -> after v1

#### Breaking Changes

Previously, jib-maven-plugin was defined inside the project poms, yet now it isn't. All projects need to have their usages of mvn_docker_image.yml@main updated to mvn_docker_image.yml@v1 or do the following changes in their poms:

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