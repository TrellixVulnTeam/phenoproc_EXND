from __future__ import print_function

from flask_login import login_required, current_user
from ..models import Permission, Role, User, Workflow, WorkItem, DataSource, Data, DataType, OperationSource, Operation
from ..operations import execute_workflow
from flask import current_app
from ..util import Utility
from .. import db

class WorkflowHandler:
    @staticmethod
    def run_workflow(obj_response, workflow_id):
        workflow_id = Utility.ValueOrNone(workflow_id)
        if workflow_id is not None and Workflow.query.get(workflow_id) is not None:
            execute_workflow(workflow_id)
    
    @staticmethod        
    def set_editmode(obj_response, mode):
        current_app.config['WORKFLOW_MODE_EDIT'] = mode
    
    @staticmethod        
    def add_workflow(obj_response):
        if current_user.is_authenticated:
            workflow = Workflow(user_id=current_user.id, name='New Workflow')            
            db.session.add(workflow)
            db.session.commit()
            obj_response.redirect(request.base_url + '{0}{1}'.format('?workflow=', workflow.id))
    
    @staticmethod        
    def delete_workflow(obj_response, workflow_id):
#        print(request.base_url, file=sys.stderr)
        if current_user.is_authenticated:
            workflow_id = Utility.ValueOrNone(workflow_id)
            if workflow_id is not None and Workflow.query.get(workflow_id) is not None:
                Workflow.query.filter(Workflow.id == workflow_id).delete()
                db.session.commit()
                obj_response.redirect('/')
                
    @staticmethod        
    def delete_workitem(obj_response, workitem_id):
        if current_user.is_authenticated:
             workitem_id = Utility.ValueOrNone(workitem_id)
             if workitem_id is not None and WorkItem.query.get(workitem_id) is not None:
                WorkItem.query.filter(WorkItem.id == workitem_id).delete()
                db.session.commit()               
                                              
    @staticmethod        
    def add_workitem(obj_response, wf_id):
        if current_user.is_authenticated:
            wf_id = Utility.ValueOrNone(wf_id)
            if wf_id is not None and Workflow.query.get(wf_id) is not None:
                workitem = WorkItem(workflow_id=wf_id, name='New Workitem')            
                db.session.add(workitem)
                db.session.commit()
    
    @staticmethod        
    def add_input(obj_response, datasource, path, workitem_id):
        if current_user.is_authenticated:
            workitem_id = Utility.ValueOrNone(workitem_id)
            datasource = Utility.ValueOrNone(datasource)
            current_app.config['WORKFLOW_MODE_EDIT']
            if workitem_id is not None and WorkItem.query.get(workitem_id) is not None:
                workitem = WorkItem.query.get(workitem_id)
                data = Data.query.filter_by(url = path).first()
                if data is None:
                    data = Data(datasource_id = datasource, datatype=DataType.Unknown, url = path)
                workitem.inputs = data
                db.session.commit()
                
    @staticmethod        
    def add_output(obj_response, datasource, path, workitem_id):
        if current_user.is_authenticated:
            workitem_id = Utility.ValueOrNone(workitem_id)
            datasource = Utility.ValueOrNone(datasource)
            print(path)
            if workitem_id is not None and WorkItem.query.get(workitem_id) is not None:
                workitem = WorkItem.query.get(workitem_id)            
                data = Data.query.filter_by(url = path).first()
                if data is None:
                    data = Data(datasource_id = datasource, datatype = DataType.Unknown, url = path)
                workitem.outputs = data
                db.session.commit()
                
    @staticmethod        
    def add_operation(obj_response, workitem_id, operation_id):
        if current_user.is_authenticated:
            workitem_id = Utility.ValueOrNone(workitem_id)
            operation_id = Utility.ValueOrNone(operation_id)
            
            if workitem_id is not None and WorkItem.query.get(workitem_id) is not None and Operation.query.get(operation_id) is not None:
                workitem = WorkItem.query.get(workitem_id)
                workitem.operation = Operation.query.get(operation_id)
                print(workitem.operation.id)
                db.session.commit()

    @staticmethod        
    def update_workflow(obj_response, workflow_id, workflow_name):
        if current_user.is_authenticated and current_app.config['WORKFLOW_MODE_EDIT']:
             workflow_id = Utility.ValueOrNone(workflow_id)
             if workflow_id is not None and Workflow.query.get(workflow_id) is not None:
                Workflow.query.get(workflow_id).name = workflow_name
                db.session.commit()               
    
    @staticmethod        
    def update_workitem(obj_response, workitem_id, workitem_name):
        if current_user.is_authenticated and current_app.config['WORKFLOW_MODE_EDIT']:
             workitem_id = Utility.ValueOrNone(workitem_id)
             if workitem_id is not None and WorkItem.query.get(workitem_id) is not None:
                WorkItem.query.get(workitem_id).name = workitem_name
                db.session.commit()