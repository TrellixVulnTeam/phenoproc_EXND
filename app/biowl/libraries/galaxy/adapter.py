from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.histories import HistoryClient
from bioblend.galaxy.libraries import LibraryClient
from bioblend.galaxy.tools import ToolClient
from bioblend.galaxy.datasets import DatasetClient
from bioblend.galaxy.jobs import JobsClient

from urllib.parse import urlparse, urlunparse
import urllib.request
import shutil
import json
import uuid
import tempfile
from ftplib import FTP
from collections import namedtuple
import os
import time

from flask import current_app


from ...fileop import IOHelper, PosixFileSystem
from ....util import Utility

#gi = GalaxyInstance(url='http://sr-p2irc-big8.usask.ca:8080', key='7483fa940d53add053903042c39f853a')
#  r = toolClient.run_tool('a799d38679e985db', 'toolshed.g2.bx.psu.edu/repos/devteam/fastq_groomer/fastq_groomer/1.0.4', params)
srlab_galaxy = 'http://sr-p2irc-big8.usask.ca:8080'
srlab_key='7483fa940d53add053903042c39f853a'

galaxies = {}

def get_galaxy_server(*args):
    return args[0] if len(args) > 0 and args[0] is not None else srlab_galaxy

def get_galaxy_key(*args):
    return args[1] if len(args) > 1 and args[1] is not None else srlab_key

def get_galaxy_instance(server, key):
    if (server, key) in galaxies:
        return galaxies[(server, key)]
    
    gi = GalaxyInstance(server, key)
    galaxies[(server, key)] = gi
    return gi

def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())

def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)

def create_galaxy_instance(*args):
    server = get_galaxy_server(*args)
    key = get_galaxy_key(*args)
    return get_galaxy_instance(server, key)

#workflow  
def get_workflows_json(*args):
    gi = create_galaxy_instance(*args)
    return gi.workflows.get_workflows()
    
def get_workflow_ids(*args):
    wf = get_workflows_json(*args)
    wf_ids = []
    for j in wf:
        #yield j.name
        wf_ids.append(j['id'])
    return wf_ids

def get_workflow_info(*args):
    gi = create_galaxy_instance(*args)
    workflows = gi.get_workflows(workflow_id=args[3])
    return workflows[0] if workflows else None

def run_workflow(*args):
    gi = create_galaxy_instance(*args)
    workflow_id = args[3]
    datamap = dict()
    datamap['252'] = { 'src':'hda', 'id':str(args[4]) }
    return gi.workflows.run_workflow(args[3], datamap, history_name='New Workflow Execution History')

#library       
def get_libraries_json(*args):
    gi = create_galaxy_instance(*args)
    return gi.libraries.get_libraries()
    
def get_library_ids(*args):
    wf = get_libraries_json(*args)
    wf_ids = []
    for j in wf:
        #yield j.name
        wf_ids.append(j['id'])
    return wf_ids

def get_library_info(*args):
    gi = create_galaxy_instance(*args)
    libraries = gi.libraries.get_libraries(library_id = args[3])
    return libraries[0] if libraries else None

def create_library(*args):
    gi = create_galaxy_instance(*args)
    name = args[3] if len(args) > 3 else str(uuid.uuid4())
    library = gi.libraries.create_library(name)
    return library["id"]

#history
def get_histories_json(*args):
    gi = create_galaxy_instance(*args)
    return gi.histories.get_histories()
    
def get_history_ids(*args):
    histories = get_histories_json(*args)
    history_ids = []
    for h in histories:
        #yield j.name
        history_ids.append(h['id'])
    return history_ids

def get_history_info(*args):
    gi = create_galaxy_instance(*args)
    histories = gi.histories.get_histories(history_id = args[3])
    return histories[0] if histories else None
  
def get_most_recent_history(*args):
    gi = create_galaxy_instance(*args)
    hi = gi.histories.get_most_recently_used_history()
    return hi['id']
        
def create_history(*args):
    gi = create_galaxy_instance(*args)
    historyName = args[3] if len(args) > 3 else str(uuid.uuid4())
    h = gi.histories.create_history(historyName)
    return h["id"]

def history_id_to_name(*args):
    info = get_history_info(*args)
    if info:
        return info['name']

def history_name_to_ids(*args):
    gi = create_galaxy_instance(*args)
    histories = gi.histories.get_histories(name = args[3])
    history_ids = []
    for history in histories:
        history_ids.append(history['id'])
    return history_ids

#tool        
def get_tools_json(*args):
    gi = create_galaxy_instance(*args)
    return gi.tools.get_tools()

def get_tool_ids(*args):
    tools = get_tools_json(*args)
    tool_ids = []
    for t in tools:
        #yield j.name
        tool_ids.append(t['id'])
    return tool_ids
   
def get_tool_info(*args):
    gi = create_galaxy_instance(*args)
    tools = gi.tools.get_tools(tool_id = args[3])
    if tools:
        return tools[0]

def tool_id_to_name(*args):
    tool = get_tool_info(*args)
    if tool:
        return tool['name']

def tool_name_to_ids(*args):
    gi = create_galaxy_instance(*args)
    tools = gi.tools.get_tools(name = args[3])
    tool_ids = []
    for t in tools:
        tools_ids.append(t['id'])
    return tool_ids

def get_tool_names(*args):
    tools = get_tools_json(*args)
    tool_names = []
    for t in tools:
        #yield j.name
        tool_names.append(t['name'])
    return tool_names
                          
def get_tool_params(*args):
    gi = create_galaxy_instance(*args)
    ts = gi.tools.show_tool(tool_id = args[3], io_details=True)
    return ts[args[4]]  if len(args) > 4 else ts
 
# dataset                                       
def get_history_datasets(*args):
    gi = create_galaxy_instance(*args)
    historyid = args[3] if len(args) > 3 else get_most_recent_history(gi)
    name = args[4] if len(args) > 4 else None

    datasets = gi.histories.show_matching_datasets(historyid, name)
    ids = []
    for dataset in datasets:
        ids.append(dataset['id'])
    return ids
                          
def dataset_id_to_name(*args):
    gi = create_galaxy_instance(*args)
    t = args[4] if len(args) > 4 else 'hda'
    info = gi.datasets.show_dataset(dataset_id = args[3], hda_ldda = t)
    if info:
        return info['name']

def dataset_name_to_ids(*args):
    gi = create_galaxy_instance(*args)
    h = HistoryClient(gi)
    historyid = args[4] if len(args) > 4 else get_most_recent_history(*args)
    ds_infos = h.show_matching_datasets(historyid, args[3])
    ids = []
    for info in ds_infos:
        ids.append(info['id'])
    return ids

# def upload(*args):
#     gi = create_galaxy_instance(*args)
#     library = get_library(*args)
#     if library is not None:
#         return gi.libraries.upload_file_from_local_path(library['id'], args[4])
#     else:
#         r = gi.tools.upload_file(args[4], args[3])
    
def upload_to_library_from_url(*args):
    gi = create_galaxy_instance(*args)
    d = gi.libraries.upload_file_from_url(args[4], args[3])
    return d["id"]

def http_to_history(remote_name, destfile):
    with urllib.request.urlopen(remote_name) as response, open(destfile, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

def wait_for_job_completion(gi, job_id):
    jc = JobsClient(gi)
    state = jc.get_state(job_id)
    while state != 'ok':
        time.sleep(0.5)
        state = jc.get_state(job_id)
    return jc.show_job(job_id)  
        
def ftp_download(u, destfile):       
    ftp = FTP(u.netloc)
    ftp.login()
    ftp.cwd(os.path.dirname(u.path))
    ftp.retrbinary("RETR " + os.path.basename(u.path), open(destfile, 'wb').write)

def fs_upload(local_file, history_id, library_id, *args):
    gi = create_galaxy_instance(*args)

    if library_id is not None:
        return gi.libraries.upload_file_from_local_path(library_id, local_file)
    else:
        return gi.tools.upload_file(local_file, history_id)

def temp_file_from_urlpath(u):
    filename = os.path.basename(u.path)   
    destfile = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(destfile):
        os.remove(destfile)
    return destfile
    
def ftp_upload(u, history_id, library_id, *args):
    
    srcFTP = ftplib.FTP(u.netloc)
    srcFTP.login()
    srcFTP.cwd(os.path.dirname(u.path))
    srcFTP.voidcmd('TYPE I')
    
    try:
        destFTP = ftplib.FTP("sr-p2irc-big8.usask.ca", 'phenodoop', 'sr-hadoop')
        destFTP.login()
        destFTP.cwd("galaxy_import")
        destFTP.voidcmd('TYPE I')
        
        from_Sock = srcFTP.transfercmd("RETR " + os.path.basename(u.path))
        to_Sock = destFTP.transfercmd("STOR " + os.path.basename(u.path))
        
        state = 0
        while 1:
            block = from_Sock.recv(1024)
            if len(block) == 0:
                break
            state += len(block)
            while len(block) > 0:
                sentlen = to_Sock.send(block)
                block = block[sentlen:]     
        
        from_Sock.close()
        to_Sock.close()
        srcFTP.quit()
        destFTP.quit()
        
        gi = create_galaxy_instance(*args)
        if library_id:
            return gi.libraries.upload_file_from_server(library_id, 'galaxy_import')
        else:
            libs = gi.libraries.get_libraries(name='import_dir')
            if not libs:
                lib = gi.libraries.create_library(name='import_dir')
            else:
                lib = libs[0]
            d = gi.libraries.upload_file_from_server(lib['id'], 'galaxy_import')
            job_info = wait_for_job_completion(gi, d['jobs'][0]['id'])
            id = job_info['outputs']['output0']['id']
            dataset = gi.histories.import_dataset([id])
            return dataset['id']
    except:
        destfile = temp_file_from_urlpath(u)
        ftp_download(u, destfile)
        fs_upload(destfile , history_id, library_id, *args)

def get_normalized_path(path):
    path = Utility.get_quota_path(path)
    fs = PosixFileSystem(Utility.get_rootdir(2))       
    return fs.normalize_path(path)
              
def local_upload(history_id, library_id, *args):
    u = urlparse(args[3])
        
    job = None
    if u.scheme:
        if u.scheme.lower() == 'http' or u.scheme.lower() == 'https':
            tempfile = temp_file_from_urlpath(u)
            http_to_history(args[3], tempfile)
            job = fs_upload(tempfile, history_id, library_id, *args)
            return job['outputs'][0]['id']
        elif u.scheme.lower() == 'ftp':
            if get_galaxy_server(*args) == srlab_galaxy:
                return ftp_upload(u, history_id, library_id, *args)
        else:
            raise 'No http(s) or ftp addresses given.'
    else:
        job = fs_upload(get_normalized_path(path), history_id, library_id, *args)
        return job['outputs'][0]['id']
    
    job_info = wait_for_job_completion(gi, job['jobs'][0]['id'])
    return job_info['outputs']['output0']['id']

def upload(*args):
    tempargs = args[:3]
    library_id = None
    history_id = None
    if len(args) > 4:
        tempargs.append(args[4])
        library = get_library_info(*tempargs)
        if library:
            library_id = library['id']
            
    if not library_id:
        history_id = args[4] if len(args) > 4 else get_most_recent_history(*args)
    
    return local_upload(history_id, library_id, *args)
    
def run_tool(*args):
    gi = create_galaxy_instance(*args)
    toolClient = ToolClient(gi)
    #params = json2obj(args[5])
    inputs = args[5] #json.loads(args[5]) if len(args) > 5 else None
#     if params:
#         params = params.split(",")
#         for param in params:
#             param = param.split(":")
#             inputs[str(param[0]).strip()] = param[1]
            
    d = toolClient.run_tool(history_id=args[3], tool_id=args[4], tool_inputs=inputs)
    job_info = wait_for_job_completion(gi, d['jobs'][0]['id'])
    return job_info#['outputs']['output_file']['id']


#===============================================================================
# run_fastq_groomer
# {"tool_id":"toolshed.g2.bx.psu.edu/repos/devteam/fastq_groomer/fastq_groomer/1.0.4",
# "tool_version":"1.0.4",
# "inputs":{"input_file":{"values":[{"src":"hda","name":"SRR034608.fastq","tags":[],"keep":false,"hid":1,"id":"c9468fdb6dc5c5f1"}],"batch":false},
# "input_type":"sanger","options_type|options_type_selector":"basic"}}
#===============================================================================
def run_fastq_groomer(*args):
    
    historyid = args[4] if len(args) > 4 else get_most_recent_history(*args)
#    historyid = get_most_recent_history(*args)

#     dataset_ids = dataset_name_to_ids(*args)
#     if len(dataset_ids) == 0:
#         raise "Input dataset not found"

#     dataset_id = dataset_ids[0]
    input = {"input_file":{"values":[{"src":"hda", "id":args[3]}]}}

    server_args = list(args[:3])
    server_args.append('FASTQ Groomer')
    tool_ids = tool_name_to_ids(*server_args)
    if not tool_ids:
        raise 'Tool FASTQ Groomer not found'
    tool_args = list(args[:3])
    tool_args.extend([historyid, tool_ids[0], input])

    output = run_tool(*tool_args)
    return output['outputs']['output_file']['id']

#===============================================================================
# run_bwa
# {"tool_id":"toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa/0.7.15.2","tool_version":"0.7.15.2",
# "inputs":{
#     "reference_source|reference_source_selector":"history",
#     "reference_source|ref_file":{
#         "values":[{
#             "src":"hda",
#             "name":"all.cDNA",
#             "tags":[],
#             "keep":false,
#             "hid":2,
#             "id":"0d72ca01c763d02d"}],
#         "batch":false},
#         "reference_source|index_a":"auto",
#         "input_type|input_type_selector":"paired",
#         "input_type|fastq_input1":{
#             "values":[{
#                 "src":"hda",
#                 "name":"FASTQ Groomer on data 1",
#                 "tags":[],
#                 "keep":false,
#                 "hid":10,
#                 "id":"4eb81b04b33684fd"}],
#             "batch":false
#         },
#     "input_type|fastq_input2":{
#         "values":[{
#             "src":"hda",
#             "name":"FASTQ Groomer on data 1",
#             "tags":[],
#             "keep":false,
#             "hid":11,
#             "id":"5761546ab79a71f2"}],
#         "batch":false
#     },
#     "input_type|adv_pe_options|adv_pe_options_selector":"do_not_set",
#     "rg|rg_selector":"do_not_set",
#     "analysis_type|analysis_type_selector":"illumina"
#     }
#===============================================================================
def run_bwa(*args):
    
    historyid = args[6] if len(args) > 6 else get_most_recent_history(*args)
#     historyid = get_most_recent_history(*args)
    
#     ref_datasetargs = list(args[:4])
#     ref_datasetargs.append(historyid)
#     refdataset_ids = dataset_name_to_ids(*args)
#     if len(refdataset_ids) == 0:
#         raise "Reference dataset not found"
#     
#     datasetargs = list(args[:3])
#     datasetargs.append(args[5])
#     dataset_ids1 = dataset_name_to_ids(*args)
#     if len(dataset_ids1) == 0:
#         raise "Pair1 dataset not found"
#     
#     datasetargs = list(args[:3])
#     datasetargs.append(args[6])
#     dataset_ids2 = dataset_name_to_ids(*args)
#     if len(dataset_ids2) == 0:
#         raise "Pair2 dataset not found"

#     dataset_id1 = dataset_ids1[0]
#     dataset_id2 = dataset_ids2[0]
#     refdataset_id = refdataset_ids[0]

    refdataset_id = args[3]
    dataset_id1 = args[4]
    dataset_id2 = args[5]
    
    input = {
     "reference_source|reference_source_selector":"history",
     "reference_source|ref_file":{
         "values":[{
             "src":"hda",
#              "name":"all.cDNA",
             "tags":[],
#             "keep":False,
#              "hid":2,
             "id":refdataset_id}],
         "batch":False},
         "reference_source|index_a":"auto",
         "input_type|input_type_selector":"paired",
         "input_type|fastq_input1":{
             "values":[{
                 "src":"hda",
#                 "name":"FASTQ Groomer on data 1",
                 "tags":[],
#                 "keep":False,
#                  "hid":10,
                 "id": dataset_id1}],
             "batch":False
         },
     "input_type|fastq_input2":{
         "values":[{
             "src":"hda",
#             "name":"FASTQ Groomer on data 1",
             "tags":[],
#             "keep":False,
#              "hid":11,
             "id": dataset_id2}],
         "batch":False
     },
     "input_type|adv_pe_options|adv_pe_options_selector":"do_not_set",
     "rg|rg_selector":"do_not_set",
     "analysis_type|analysis_type_selector":"illumina"
     }

    server_args = list(args[:3])
    server_args.append('Map with BWA')
    tool_ids = tool_name_to_ids(*server_args)
    if not tool_ids:
        raise 'Tool not found'
    tool_args = list(args[:3])
    tool_args.extend([historyid, tool_ids[0], input])

    output = run_tool(*tool_args)
#     {'model_class': 'Job', 
#      'outputs': {
#          'bam_output': {
#              'src': 'hda', 'id': '7b326180327c3fcc', 'uuid': 'ccfaaa0a-946a-4a51-87b0-bdf71f13f3e6'
#           }
#       }, 
#      'state': 'ok', 
#      'create_time': '2017-10-12T11:13:34.731974', 
#      'command_line': 'ln -s "/home/phenodoop/galaxy/galaxy/database/files/000/dataset_105.dat" "localref.fa" && bwa index "localref.fa" &&                 bwa aln -t "${GALAXY_SLOTS:-1}"     "localref.fa"  "/home/phenodoop/galaxy/galaxy/database/files/000/dataset_203.dat"  > first.sai &&  bwa aln -t "${GALAXY_SLOTS:-1}"     "localref.fa"  "/home/phenodoop/galaxy/galaxy/database/files/000/dataset_203.dat"  > second.sai &&  bwa sampe      "localref.fa" first.sai second.sai "/home/phenodoop/galaxy/galaxy/database/files/000/dataset_203.dat" "/home/phenodoop/galaxy/galaxy/database/files/000/dataset_203.dat"    | samtools sort -O bam -o \'/home/phenodoop/galaxy/galaxy/database/files/000/dataset_208.dat\'', 'id': 'd448712f90897b61', 
#      'inputs': {'fastq_input2': {'src': 'hda', 'id': 'dfd15528ee538abe', 'uuid': '88502312-ba9a-4f2a-bacb-05bf176e69e7'}, 
#                 'fastq_input1': {'src': 'hda', 'id': 'dfd15528ee538abe', 'uuid': '88502312-ba9a-4f2a-bacb-05bf176e69e7'}, 
#                 'ref_file': {'src': 'hda', 'id': '7ef8021ae23ac2fc', 'uuid': 'ba22f14a-18bc-410e-ab76-160b41584436'}}, 
#      'update_time': '2017-10-12T11:16:29.151400', 'tool_id': 'toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa/0.7.15.2', 'exit_code': 0, 'external_id': '429', 
#      'params': {'input_type': '{"adv_pe_options": {"__current_case__": 1, "adv_pe_options_selector": "do_not_set"}, "fastq_input2": {"values": [{"src": "hda", "id": 204}]}, "__current_case__": 0, "input_type_selector": "paired", "fastq_input1": {"values": [{"src": "hda", "id": 204}]}}', 'rg': '{"rg_selector": "do_not_set", "__current_case__": 3}', 'dbkey': '"?"', 'chromInfo': '"/home/phenodoop/galaxy/galaxy/tool-data/shared/ucsc/chrom/?.len"', 'analysis_type': '{"analysis_type_selector": "illumina", "__current_case__": 0}', 'reference_source': '{"ref_file": {"values": [{"src": "hda", "id": 205}]}, "reference_source_selector": "history", "__current_case__": 1, "index_a": "auto"}'}}
    return output['outputs']['bam_output']['id']

def download(*args):
    gi = create_galaxy_instance(*args)
    
    dataset = gi.datasets.show_dataset(dataset_id = args[3], hda_ldda = 'hda')
    name = dataset['name']
    
    path = get_normalized_path(args[4] if len(args) > 4 else None)
    fullpath = os.path.join(path, name)
    gi.datasets.download_dataset(args[3], file_path = fullpath, use_default_filename=False, wait_for_completion=True)
    return path
