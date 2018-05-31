from django.test import TestCase, RequestFactory, Client
from unittest import skip, expectedFailure

from datetime import timedelta

import alert_config_app.views as views
from alert_config_app.models import *
from account_mgr_app.models import *
from django.contrib.auth.models import User

from django.core.urlresolvers import reverse

# Create your tests here.
# @skip("Keeping this as an example template")
class test_alert_config_view(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.primary = User.objects.create_user("test")
        cls.primary_pass = "tests"
        cls.primary.set_password(cls.primary_pass)
        cls.primary.save()

        cls.secondary = User.objects.create_user("test2")
        cls.secondary_pass = "tests"
        cls.secondary.set_password(cls.secondary_pass)
        cls.secondary.save()

        
        cls.alerts = []
        for x in range(2):
            cls.alerts.append(Alert())
            cls.alerts[x].name = "alert_"+str(x)
            cls.alerts[x].save()
            cls.alerts[x].owner.add(cls.primary.profile)
            cls.alerts[x].save() 

        cls.factory = RequestFactory()
        cls.c = Client()
 
    def setUp(self):
        """Log the test user in before each test method.
        """
        self.c.login(
           username = self.primary.username,
           password = self.primary_pass)

    def tearDown(self):
        """Log the test user out after every test method.
        """
        self.c.logout()

    def test_create_exists(self):
        """Test that the creation page can be drawn without errors.
        """
        self.c.login(
            username = self.primary.username,
            password = self.primary_pass)
        response = self.c.get('/alert/alert_create/',follow=True)
        self.assertEqual(response.status_code, 200)

    def test_config_exists(self):
        """Test that the configuration pages can be drawn without errors.
        """
        self.c.login(
            username = self.primary.username,
            password = self.primary_pass)
        
        for single_alert in self.alerts:
            pk = single_alert.pk
            response = self.c.get(
                '/alert/alert_config/'+str(pk)+'/',
                follow=True)
            self.assertEqual(response.status_code, 200)
        self.c.logout()

    def test_config_bad_pk(self):
        """Ensure that the user is redirected after providing a bad pk value
        """
        bad_pk = 9001
        response = self.c.get('/alert/alert_config/'+str(bad_pk)+'/',
                follow=True)
        self.assertTrue(
            (reverse('alert_create'), 302) in response.redirect_chain)
        self.assertNotEqual(len(response.redirect_chain),0)

    def test_login_create(self):
        """Ensure that these pages cannot be provided to logged-out users
        """
        self.c.logout()
        response = self.c.get('/alert/alert_create/',follow=True)
        self.assertNotEqual(len(response.redirect_chain),0)

    def test_login_create(self):
        """Ensure that these pages cannot be provided to logged-out users
        """
        self.c.logout()
        for single_alert in self.alerts:
            pk = single_alert.pk
            response = self.c.get(
                '/alert/alert_config/'+str(pk)+'/',
                follow=True)
            self.assertNotEqual(len(response.redirect_chain),0)

    def test_create_template_usage(self):
        """Ensure that the creation page loads the proper templates
        """
        with self.assertTemplateUsed('alert_config.html'):
            response = self.c.get('/alert/alert_create/',follow=True)

    def test_config_template_usage(self):
        """Ensure that the config  page loads the proper templates.
        """
        for single_alert in self.alerts:
            pk = single_alert.pk
            response = self.c.get(
                '/alert/alert_config/'+str(pk)+'/',
                follow=True)

            self.assertTemplateUsed(response,'alert_config.html')

    def test_redirect_for_non_owners(self):
        """Ensure that non-owners cannot access the edit pages
        """
        self.c.logout()
        self.c.login(
            username = self.secondary.username,
            password = self.secondary_pass)

        for single_alert in self.alerts:
            pk = single_alert.pk
            response = self.c.get(
                '/alert/alert_config/'+str(pk)+'/',
                follow=True)
            self.assertNotEqual(len(response.redirect_chain),0)
            self.assertTrue(
                (reverse(
                    'alert_detail',
                    kwargs={'pk':pk}),
                302) in response.redirect_chain)
    
    def generic_alert_post(self,pk=None,*args,**kwargs):
        """Send alert creation post req. with default data and substitutions
         
        Parameter
        ---------
        pk : int, None
            database ID for modifying an alert. Passing none creates an alert
            instead of modifying one
        
        *args : unnamed arguments
            unused
        
        **kwargs : named arguments
            Substitute default post request fields with the given data
        
        Returns
        -------
        django.template.response.TemplateResponse
            the response issued from the post request
        """
        if pk==None:
            path = '/alert/alert_create/'
        else:
            path = '/alert/alert_config/{}/'.format(str(pk))
        
        
        response = self.c.get(path,follow=True)
        
        post_data = {
            "new_lockout_duration":                       "02:33:15",
                        "new_name":                 "new_alert_name",
                      "new_owners":       str(self.primary.username),
                   "new_subscribe":                             "on",
                "tg-0-new_compare":                             "<=",
                   "tg-0-new_name":                      "0 trigger",
                     "tg-0-new_value_src":                             "-1",
                  "tg-0-new_value":                            "100",
                "tg-1-new_compare":                             "==",
                   "tg-1-new_name":                      "1 trigger",
                     "tg-1-new_value_src":                             "-1",
                  "tg-1-new_value":                              "7",
                "tg-2-new_compare":                             "-1",
                   "tg-2-new_name":                               "",
                     "tg-2-new_value_src":                             "-1",
                  "tg-2-new_value":                               "",
                "tg-INITIAL_FORMS":                              "0",
                "tg-MAX_NUM_FORMS":                           "1000",
                "tg-MIN_NUM_FORMS":                              "0",
                  "tg-TOTAL_FORMS":                              "3",   
        }
        
        # add in kwargs-specified substitutions
        for x in kwargs:
            if kwargs[x] == None:
                post_data.pop(x)
            else:
                post_data[x] = kwargs[x]
        
        response = self.c.post(
            path,
            data=post_data,
            follow=True)
        return response

    def test_create_alert(self):
        """ check that alert is created correctly from this POST request
        """
        # Initiate post/get transaction
        response = self.generic_alert_post(**{'new_name':'alert_name'})
        # confirm that alert with proper name exists
        try:
            alert_inst = Alert.objects.get(name="alert_name")
        except Exception as E:
            print(E)
            self.fail("Alert not created")
         
        # confirm that the user is added as the owner
        self.assertEqual(
            len(alert_inst.owner.all()),
            1,
            "incorrect number of owners"
        )

        # confirm that the indicated user has also been added as an owner
        self.assertTrue(
            self.primary.profile in alert_inst.owner.all(),
            "indicated owner is not added as owner"
        )

            
        # confirm that primary user has also been added as a subscriber
        self.assertTrue(
            self.primary.profile in alert_inst.subscriber.all(),
            "primary owner is not added as subscriber"
        )
        
        # confirm that lockout duration has been properly added 
        self.assertEqual(
            alert_inst.lockout_duration,
            timedelta(hours=2,minutes=33,seconds=15),
            "Lockout duration has incorrect value"
        )
        
        # confirm the proper number of triggers have been created 
        self.assertEqual(
            len(alert_inst.trigger_set.all()),
            2,
            "Incorrect number of triggers created"
        )

        # ensure triggers 0 and 1 have been added 
        self.assertTrue(
            Trigger.objects.get(name="0 trigger",alert=alert_inst) in \
                    alert_inst.trigger_set.all(),
            "0 Trigger not added"
        )
        self.assertTrue(
            Trigger.objects.get(name="0 trigger",alert=alert_inst) in \
                    alert_inst.trigger_set.all(),
            "1 Trigger not added"
        )

    def test_modify_alert(self):
        """ check that alert is created correctly from this POST request
        """
        # Initiate post/get transaction
        response = self.generic_alert_post(
            new_name = "starting_name",
            **{
                "new_owners" : [
                    str(self.primary.username) +", "+
                    str(self.secondary.username),
                ],
            })
        
        try:
            alert_inst = Alert.objects.get(name="starting_name")
        except Exception as E:
            self.fail("Alert not created")
        
        response = self.generic_alert_post(
            pk = alert_inst.pk,
            **{
                "new_name " : "modified_name",
                "new_owners" : [
                    str(self.primary.username),
                ],
                "new_lockout_duration":"01:15:30",
                "tg-0-new_compare":-1,
                "tg-0-new_name":None,
                "tg-0-new_value":None,
                "tg-0-new_pv":-1,
                "tg-1-new_compare":"==",
                "tg-1-new_name":"generic_name",
                "tg-1-new_value":"5",
                "tg-1-new_pv":-1,
            }    
        )
        # confirm that alert with proper name exists
        try:
            alert_inst = Alert.objects.get(name="modified_name")
        except Exception as E:
            self.fail("Alert not created")
        

        # confirm that the user is added as the owner
        self.assertEqual(
            len(alert_inst.owner.all()),
            1,
            "incorrect number of owners"
        )
        # confirm that primary user has also been added as an owner
        self.assertTrue(
            self.primary.profile in alert_inst.owner.all(),
            "primaryl owner is not added as owner"
        )

        # confirm that secondary user has also been removed as an owner
        self.assertFalse(
            self.secondary.profile in alert_inst.owner.all(),
            "optional owner is not removed as owner"
        )
   
        # confirm that primary user has also been added as a subscriber
        self.assertTrue(
            self.primary.profile in alert_inst.subscriber.all(),
            "primary owner is not added as subscriber"
        )
        
        # confirm that lockout duration has been properly added 
        self.assertEqual(
            alert_inst.lockout_duration,
            timedelta(hours=1,minutes=15,seconds=30),
            "Lockout duration has incorrect value"
        )
        
        # confirm the proper number of triggers have been created 
        self.assertEqual(
            len(alert_inst.trigger_set.all()),
            1,
            "Incorrect number of triggers"
        )

        # ensure triggers 0 and 1 have been added 
        self.assertTrue(
            Trigger.objects.get(name="generic_name",alert=alert_inst) in \
                    alert_inst.trigger_set.all(),
            "Trigger not modified"
        )

    def test_non_owner_modification_rejection(self):
        """ensure that PRs from non-owners will be rejected
        """
        
        # Initiate post/get transaction
        response = self.generic_alert_post(
            new_name = "start_name",
            **{
                "new_owners" : [
                    str(self.primary.username)
                ],
            })
        
        try:
            alert_inst = Alert.objects.get(name="start_name")
        except Exception as E:
            self.fail("Alert not created")
        
        self.c.logout()
        self.c.login(
            username = self.secondary.username,
            password = self.secondary_pass,
        )
        
        response = self.generic_alert_post(
            pk = alert_inst.pk,
            **{
                "new_name " : "modified_name",
                "new_owners" : [
                    str(self.primary.username),
                ],
                "new_lockout_duration":"01:15:30",
                "tg-0-new_compare":-1,
                "tg-0-new_name":None,
                "tg-0-new_value":None,
                "tg-0-new_pv":-1,
                "tg-1-new_compare":"==",
                "tg-1-new_name":"generic_name",
                "tg-1-new_value":"5",
                "tg-1-new_pv":-1,
            }    
        )

        self.assertEqual(
            alert_inst.name,
            "start_name",
            "Name has been allowed to change"
        )


        self.assertTrue(
            ('/alert/alert_detail/'+str(alert_inst.pk)+'/',302) in
                response.redirect_chain,
            "Failed to redirect to detail page"
        )

    def test_create_alert_bad_owners(self):
        """ check that alert is created correctly from this POST request
        """
        # Initiate post/get transaction
        response = self.generic_alert_post(
            new_name = "owner_redirect_name",
            **{"new_owners" : None}
        )
        
        # confirm that alert with proper name exists
        try:
            alert_inst = Alert.objects.get(name="owner_redirect_name")
            self.fail("Bad alert created")
        except Exception as E:
            # This SHOULD fail as the alert should not have been created
            pass

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'alert_config.html')
        self.assertContains(response, 'owner_redirect_name')


class test_alert_detail_view(TestCase):
    """Collection of tests inspecting the detail_alert form 
    """
    @classmethod
    def setUpTestData(cls):
        cls.primary = User.objects.create_user("test")
        cls.primary_pass = "tests"
        cls.primary.set_password(cls.primary_pass)
        cls.primary.save()

        cls.secondary = User.objects.create_user("test2")
        cls.secondary_pass = "tests"
        cls.secondary.set_password(cls.secondary_pass)
        cls.secondary.save()
        
        cls.alerts = []
        for x in range(2):
            cls.alerts.append(Alert())
            cls.alerts[x].name = "alert_"+str(x)
            cls.alerts[x].save()
            cls.alerts[x].owner.add(cls.secondary.profile)
            cls.alerts[x].save() 

        cls.factory = RequestFactory()
        cls.c = Client()
    
    def setUp(self):
        """Log the test user in before each test method.
        """
        self.c.login(
           username = self.primary.username,
           password = self.primary_pass)

    def tearDown(self):
        """Log the test user out after every test method.
        """
        self.c.logout()

    def test_exists(self):
        """Ensure the detail page draws correctly for non-owners.
        """
        response = self.c.get(
            '/alert/alert_detail/'+str(self.alerts[0].pk)+'/',
            follow=True)
        self.assertEqual(response.status_code, 200, "Error code reported")
        self.assertTemplateUsed(response,'alert_detail.html', "Wrong Template")

    def test_redirection(self):
        """Ensure owners are redirected to the config page
        """
        self.c.logout()
        self.c.login(
            username = self.secondary.username,
            password = self.secondary_pass,
        )
        
        response = self.c.get(
            '/alert/alert_detail/'+str(self.alerts[0].pk)+'/',
            follow=True)
        self.assertTrue(
            ('/alert/alert_config/'+str(self.alerts[0].pk)+'/',302) in
                response.redirect_chain,
            "Failed to redirect to configuration page"
        )

    def test_post_request(self):
        """Ensure PRs accept changes from owners are rejected
        """
        self.c.logout()
        self.c.login(
            username = self.secondary.username,
            password = self.secondary_pass,
        )

        path = '/alert/alert_detail/'+str(self.alerts[0].pk)+'/'
        post_data = { 'new_subscribe':'on' }
        response = self.c.post(
            path,
            data=post_data,
            follow=True
        )
        self.assertFalse(
            self.secondary.profile in self.alerts[0].subscriber.all(),
            "subscriber added",
        )

        self.alerts[0].subscriber.add(self.secondary.profile)
        
        path =  '/alert/alert_detail/'+str(self.alerts[0].pk)+'/'
        post_data = {}
        response = self.c.post(
            path,
            data=post_data,
            follow=True
        )
        
        self.assertTrue(
            self.secondary.profile in self.alerts[0].subscriber.all(),
            "subscriber removed",
        )


    def test_post_request_non_owner(self):
        """ensure PRs from non-owners are accepted
        """
        
        path = '/alert/alert_detail/'+str(self.alerts[0].pk)+'/'
        post_data = { 'new_subscribe':'on' }
        response = self.c.post(
            path,
            data=post_data,
            follow=True
        )
        self.assertTrue(
            self.primary.profile in self.alerts[0].subscriber.all(),
            "subscriber not added",
        )

        path =  '/alert/alert_detail/'+str(self.alerts[0].pk)+'/'
        post_data = {}
        response = self.c.post(
            path,
            data=post_data,
            follow=True
        )
        
        self.assertFalse(
            self.primary.profile in self.alerts[0].subscriber.all(),
            "subscriber not removed",
        )


class test_alert_list_page_view(TestCase): 
    @classmethod
    def setUpTestData(cls):
        cls.primary = User.objects.create_user("test")
        cls.primary_pass = "tests"
        cls.primary.set_password(cls.primary_pass)
        cls.primary.save()

        cls.secondary = User.objects.create_user("test2")
        cls.secondary_pass = "tests"
        cls.secondary.set_password(cls.secondary_pass)
        cls.secondary.save()

        
        cls.alerts = []
        for x in range(2):
            cls.alerts.append(Alert())
            cls.alerts[x].name = "alert_"+str(x)
            cls.alerts[x].save()
            cls.alerts[x].owner.add(cls.primary.profile)
            cls.alerts[x].save() 

        cls.factory = RequestFactory()
        cls.c = Client()
 
    def setUp(self):
        """Log the test user in before each test method.
        """
        self.c.login(
           username = self.primary.username,
           password = self.primary_pass)

    def tearDown(self):
        """Log the test user out after every test method.
        """
        self.c.logout()
    
    def test_page_visit(self):
        response = self.c.get('/alert/alert_create/',follow=True)
        self.assertEqual(
            response.status_code,
            200,
            "Unable to render the alerts list"
        )
        

class test_title_page_view(TestCase): 
    @classmethod
    def setUpTestData(cls):
        cls.primary = User.objects.create_user("test")
        cls.primary_pass = "tests"
        cls.primary.set_password(cls.primary_pass)
        cls.primary.save()

        cls.secondary = User.objects.create_user("test2")
        cls.secondary_pass = "tests"
        cls.secondary.set_password(cls.secondary_pass)
        cls.secondary.save()

        
        cls.alerts = []
        for x in range(2):
            cls.alerts.append(Alert())
            cls.alerts[x].name = "alert_"+str(x)
            cls.alerts[x].save()
            cls.alerts[x].owner.add(cls.primary.profile)
            cls.alerts[x].save() 

        cls.factory = RequestFactory()
        cls.c = Client()
 
    def setUp(self):
        """Log the test user in before each test method.
        """
        self.c.login(
           username = self.primary.username,
           password = self.primary_pass)

    def tearDown(self):
        """Log the test user out after every test method.
        """
        self.c.logout()
    
    def test_page_visit(self):
        response = self.c.get('/alert/title/',follow=True)
        self.assertEqual(
            response.status_code,
            200,
            "Unable to render the title page"
        )



class test_alert_delete_page_view(TestCase): 
    @classmethod
    def setUpTestData(cls):
        cls.primary = User.objects.create_user("test")
        cls.primary_pass = "tests"
        cls.primary.set_password(cls.primary_pass)
        cls.primary.save()

        cls.secondary = User.objects.create_user("test2")
        cls.secondary_pass = "tests"
        cls.secondary.set_password(cls.secondary_pass)
        cls.secondary.save()

        
        cls.alerts = []
        for x in range(2):
            cls.alerts.append(Alert())
            cls.alerts[x].name = "alert_"+str(x)
            cls.alerts[x].save()
            cls.alerts[x].owner.add(cls.primary.profile)
            cls.alerts[x].save() 

        cls.factory = RequestFactory()
        cls.c = Client()
 
    def setUp(self):
        """Log the test user in before each test method.
        """
        self.c.login(
           username = self.primary.username,
           password = self.primary_pass)

    def tearDown(self):
        """Log the test user out after every test method.
        """
        self.c.logout()
    
    def test_page_visit(self):
        response = self.c.get('/alert/alert_delete/1/',follow=True)
        self.assertEqual(
            response.status_code,
            200,
            "Unable to render the alert delete page"
        )
