# Creating a Pipeline in Airflow

For this lab you will need the scripts we've been using for extracting and loading data from the last couple labs. You will need Airflow installed and able to run.

The following video should give a decently cross-platform way of getting set up with Airflow in Docker (i.e., the commands he's running should just be able to be run in PowerShell or the MacOS Terminal): https://www.youtube.com/watch?v=aTaytcxy2Ck. **A couple notes for windows users:**
* Around the 2:26 mark, the author uses the curl command. You may need to use curl.exe instead. The arguments to curl.exe should be the same as in the video.
* Around the 5:45 mark, there is a command that the author will type that only applies to Mac and Linux users. So, Windows users will not need to type the `echo -e "..." > .env` command.

You should watch the video above, as it gives good overviews of what each step is for, but in brief, the instructions are:
1. Create a folder for your work
   ```bash
   mkdir your-work-folder
   cd your-work-folder
   ```
2. Download the latest Airflow community-maintained docker-compose config (note, on Windows you'll use `curl.exe` instead of just `curl`):
   ```bash
   curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
   ```

3. Create folders for your DAGs and other Airflow necessities (logs, plugins, which we'll leave empty for now):
   ```bash
   mkdir -p dags logs plugins
   ```

4. **Skip this step if you're using Windows.** If you're on Mac or Linux, run the following (which will create a file called _.env_ containing a couple of things that Airflow needs to know about your user):
   ```bash
   echo -e "AIRFLOW_UID=$(id -u)" > .env
   ```

5. Initialize the [metadata database](https://www.astronomer.io/guides/airflow-database) for Airflow. This will set up default roles and permissions, as well as tables for the management of tasks and pipelines (DAGs):
   ```bash
   docker-compose up airflow-init
   ```

6. To see your installation working, run the following and go to http://localhost:8080 in your browser:
   ```bash
   docker-compose up
   ```
   Use username `airflow` and password `airflow` to log in.

## Configuring your containers

Once you have Airflow installed, you'll need to prepare your **_containers_** to run your pipeline code. You can think of a container as a beefed up virtual environment (one like you might create with Conda or Poetry). As such, you'll need to install the packages that are necessary to run your pipeline installed into the containers.

> If we were preparing a production pipeline that powered some critical business processes, we'd want to [build a new **_image_**](https://airflow.apache.org/docs/docker-stack/build.html) based off of the official Airflow images. You can think of an image as a blueprint for a container. Configuring and building an image beforehand allows you to relatively quickly spin up a new container, because all of your packages have already been installed into the image.
>
> For now, instead of building our own images, we'll use the pre-built Airflow community images, and install our necessary packages when we create containers from those images.

1. First, let's turn off all the example DAGs that Airflow has, just to clear up the interface (note that you can leave these example DAGs on if you want to explore; they're not going to hurt anything). Open your _docker-compose.yaml_ file and find the line that says `AIRFLOW__CORE__LOAD_EXAMPLES: 'true'`. Change this to `AIRFLOW__CORE__LOAD_EXAMPLES: 'false'`.

2. Next, let's specify the requirements that we want to be installed when the container starts up. We're going to specify what versions of those requirements to install as well (I've tested these versions to be compatible with the Airflow 2.2.0 images). In your _docker-compose.yaml_ file, find the line that says `_PIP_ADDITIONAL_REQUIREMENTS: ${_PIP_ADDITIONAL_REQUIREMENTS:-}`. Replace that line with the following:

   ```
   _PIP_ADDITIONAL_REQUIREMENTS: "requests==2.26.0 pandas==1.1.5 google-cloud-storage==1.42.3 SQLAlchemy==1.3.20 sqlalchemy-bigquery==1.2.0 python-dotenv==0.19.1 google-cloud-bigquery-storage==2.9.1"
   ```

3. Below the `_PIP_ADDITIONAL_REQUIREMENTS` line, add a few more environment variables to the container.
   * `PIPELINE_DATA_BUCKET` -- The name of the Google Cloud Storage bucket where your data will go (if you do not already have a GCS bucket created, you will need to do so)
   * `PIPELINE_PROJECT` -- The ID of your Google Cloud Platform project (you can locate your project ID with [these instructions](https://support.google.com/googleapi/answer/7014113?hl=en))
   * `PIPELINE_DATASET` -- The name of the BigQuery dataset within your project where you will write the final tables

   For example, in my _docker-compose.yaml_ file, my variables look like this:

   ```
   PIPELINE_DATA_BUCKET: mjumbewu_cloudservices
   PIPELINE_PROJECT: musa-509-2021
   PIPELINE_DATASET: lab06
   ```

   Your values will be different, depending on what you name your bucket, project, and dataset. Ensure that the indentation matches the other environment variable lines.

4. Finally, make the Google application credentials available to the containers. Add one more line to the environment variables section:

   ```
   GOOGLE_APPLICATION_CREDENTIALS: /opt/google-app-creds.json
   ```

   Then, under the next section (labeled `volumes`) we will tell Docker to look for our Google app credentials file at _/opt/google-app-creds.json_. For this, you will need the path to your own credentials JSON file. You will add a line in the `volumes` section in the format:

   ```
   - /PATH/TO/YOUR/CREDENTIALS.json:/opt/google-app-creds.json
   ```

   For example, on my computer, my credentials file is located at _/home/mjumbewu/.google-cloud/musa-509-2021-82382711a91a.json_, so I added the following line:

   ```
   - /home/mjumbewu/.google-cloud/musa-509-2021-82382711a91a.json:/opt/google-app-creds.json
   ```


## The `pipeline_tools` module

I've provided a `pipeline_tools` module that has three functions. You should be able to read and understand each line in this module. If there is anything that is unclear, please ask for clarification.


## Creating your DAG

To run the steps of our pipeline, we're going to create a new DAG. All DAGs live in the _dags/_ folder that you created in a previous step. I recommend creating a _**package**_ for each of your DAGs. Remember that a pacakge is just a folder with a file called `__init__.py`.

1. Create a folder under _dags/_ named _addresses_pipeline/_. Within that folder, create a file named `__init__.py`.

2. Move the three `pipeline_...` modules into the _addresses_pipeline/_ folder. Since these modules are going to be specific to this data pipeline, it makes sense for them to live in the data pipeline DAG's package.

3. Move the `pipeline_tools.py` module into the _plugins/_ folder that you created earlier. Since this module could be useful for other DAGs as well, it makes sense to put it in the _plugins/_ folder, since all DAGs will be able to import modules and packages located there.

4. In the `__init__.py` file under _addresses_pipeline/_, add an `import` section. We will need to import the `DAG` class, as well as the `PythonOperator` class, both from Airflow itself. Each bit of work ([task](https://airflow.apache.org/docs/apache-airflow/stable/concepts/tasks.html)) in Airflow is defined by some ["operator"](https://airflow.apache.org/docs/apache-airflow/stable/concepts/operators.html). In this case, we're going to run the Python functions in these modules by using `PythonOperator` tasks:

   ```python
   from airflow import DAG
   from airflow.operators.python import PythonOperator
   ```

   > Note that Airflow has a couple of ways of defining a DAG and it's tasks. The way we're using today is the traditional way. As of Airflow 2.0, there is also a way called [Task Flow](https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html).

5. We will also need to import our pipeline modules. Since they are located in the same package as the `__init__.py` file, we can use what is called a relative import. The syntax "`from . import ...`" essentially means "import a module from the same package where the current module lives":
   ```python
   from . import pipeline_01_download_addresses
   from . import pipeline_02_geocode_addresses
   from . import pipeline_03_insert_addresses
   ```

6. After your imports, use the `with` keyword to define a DAG object:

   ```python
   with DAG(dag_id='addresses_pipeline',
            schedule_interval='@daily',
            start_date=datetime(2021, 10, 22),
            catchup=False) as dag:
   ```
   Here, we are creating a DAG named `addresses_pipeline`, and instructing Airflow to run this DAG on a daily basis (by default at midnight UTC each day). The `start_date` can be any day before today. Note that it uses the `datetime` class, so we will need to add the following to our import block:

   ```python
   from datetime import datetime
   ```

   > There are a [whole host of options](https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html#instantiate-a-dag) that you can choose when creating an Airflow DAG. There's an entire book written on Airflow (_Data Pipelines with Apache Airflow_, available through O'Rielly's online learning portal); lots of depth that you could dive into.

7. Next you'll define your tasks. In this case you'll have three tasks. Let's name them `extract_raw_addresses`, `extract_geocoded_addresses`, and `load_address_data`. The first one will look like:

   ```python
       extract_raw_addresses = PythonOperator(
           task_id='extract_raw_addresses',
           python_callable=pipeline_01_download_addresses.main,
       )
   ```

   The next two will be similar. Add them all inside the `with` block.

6. Finally, define the chain of dependency between the tasks with the following line (also inside of the DAG's `with` block):

   ```python
       extract_raw_addresses >> extract_geocoded_addresses >> load_address_data
   ```

After performing the above steps, reload your Airflow interface and enable the DAG. Make sure that it runs successfully. If it does not, select the failing tasks and review the errors in the logs.
