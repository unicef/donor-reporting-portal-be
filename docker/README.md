Docker images
=============================

[![](https://images.microbadger.com/badges/version/unicef/donor_reporting_portal.svg)](https://microbadger.com/images/unicef/donor_reporting_portal)

To build docker image simply cd in `docker` directory and run 

    make build
    
default settings are for production ready environment, check `run` target in 
the `Makefile` to see how to run the container with debug/less secure configuration

Image provides following services:

    - donor_reporting_portal   
    # - celery workers
    # - celery beat

to configure which services should be started, set `SERVICES` appropriately, ie:


    docker run \
        ...
        -e SERVICES="redis,workers,beat,donor_reporting_portal,flower"
        
**Note** If `SERVICES` is empty internal `supervisord` daemon does not start. 
