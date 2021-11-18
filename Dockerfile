# 0. base image
ARG BLD_BASE_IMG=continuumio/miniconda3
FROM ${BLD_BASE_IMG}
RUN chmod a+trwx /tmp
RUN apt-get update
RUN apt-get install git
ARG BLD_PROJECT_NAME='project'
ARG BLD_WORKDIR='project'


# 1. create startup scripts
RUN conda init bash
RUN cp ~/.bashrc ~/_.bashrc
RUN cp ~/_.bashrc ~/project.bashrc
RUN cp ~/_.bashrc ~/${BLD_WORKDIR}.bashrc
RUN echo "conda activate ${BLD_PROJECT_NAME}-project"           >> ~/project.bashrc
RUN echo "conda activate ${BLD_PROJECT_NAME}-${BLD_WORKDIR}"    >> ~/${BLD_WORKDIR}.bashrc
# RUN echo "cd /${BLD_PROJECT_NAME}/project"                      >> ~/project.bashrc
RUN echo "cd /${BLD_PROJECT_NAME}"                              >> ~/project.bashrc
RUN echo "cd /${BLD_PROJECT_NAME}/${BLD_WORKDIR}"               >> ~/${BLD_WORKDIR}.bashrc

COPY . /${BLD_PROJECT_NAME}
# 2. bootstrap
WORKDIR /${BLD_PROJECT_NAME}
RUN apt-get install dos2unix
RUN dos2unix ./bootstrap.sh
RUN chmod +x ./bootstrap.sh
RUN ./bootstrap.sh

# 3. set up
RUN cp ~/project.bashrc ~/.bashrc
# SHELL [ "/bin/bash", "--login", "-c"]
RUN ./project/wbin/project work-dir.setup.build --work-dir ${BLD_WORKDIR}


# 4. set/fix intended work env
RUN cp ~/${BLD_WORKDIR}.bashrc ~/.bashrc
