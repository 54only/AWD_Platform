import batch
import flagfresher
import os
import models


#os.system('/bin/bash -c "docker volume rm $(docker volume ls -qf dangling=true)"')
# docker volume rm $(docker volume ls -qf dangling=true)

teams = 10



models.main(teams)
batch.start_awd()
flagfresher.main()

