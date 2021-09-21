import logging
from typing import Optional

from django.contrib.contenttypes.forms import generic_inlineformset_factory

from django.db.models import Model
from django.forms import ModelForm, inlineformset_factory
from django.shortcuts import render, redirect

from myhouse_admin.forms.forms import MainPageForm
from myhouse_admin.models import MainPage, Block


logger = logging.getLogger(__name__)


class ProcessSingletonModel:
    '''
    class for processing for creation or update info for singleton models
    '''
    def __init__(self, *, model: Model, form_class: ModelForm, 
        template_name: str,
        success_url: str,
        request,
        generic_model: Optional[Model]=None, 
        generic_form_prefix=None, 
        generic_extra_forms=0,
        first_related_model_form=None,
        first_related_model_form_prefix=None,
        second_related_model_form=None,
        second_related_model_form_prefix=None,
        first_related_model_in_formset=None,
        first_related_model_in_formset_fields=None):

        self._model = model
        self._form_class = form_class
        self._generic_model = generic_model
        self._generic_form_prefix = generic_form_prefix
        self._generic_extra_forms = generic_extra_forms
        self._first_related_model_form = first_related_model_form
        self._first_related_model_form_prefix = first_related_model_form_prefix
        self._second_related_model_form = second_related_model_form
        self._second_related_model_form_prefix = second_related_model_form_prefix,
        self._first_related_model_in_formset = first_related_model_in_formset
        self._first_related_model_in_formset_fields = first_related_model_in_formset_fields


    def get_filled_forms(self, *, post_dict, method, files_dict=None):
        self._object = self._model.objects.first()
        if self._object is not None:
            return self._update_object(instance=self._object, post_dict=post_dict, files_dict=files_dict, method=method)
        else:
            return self._create_object(post_dict=post_dict, files_dict=files_dict, method=method)

    def _update_object(self, *, instance, post_dict, files_dict=None, method):
        '''
        method for updating object in singleton model
        return values in next order -> 
            tuple(
                redirect_available: bool, 
                form: form object of self._form_class, 
                generic_formset:Optional[filled formset],
                first_related_model_form: form object,
                second_related_model_form: form object)
        '''

        redirect_available = False
        form = self._form_class(instance=instance)
        
        # generic formset block
        generic_formset = None
        if self._generic_model is not None:
            GenericFormset = generic_inlineformset_factory(self._generic_model, can_delete=True, extra=0)
            generic_formset = GenericFormset(post_dict or None, files_dict or None, 
                queryset=instance.get_all_generic_relation, instance=instance, prefix=self._generic_form_prefix)

        if method == 'POST':
            form = self._form_class(post_dict, files_dict, instance=instance)
            is_valid = False

            if generic_formset is not None:
                is_valid = form.is_valid() and generic_formset.is_valid()
            else:
                is_valid = form.is_valid()
            if is_valid:
                form.save()
                generic_formset.save() if generic_formset is not None else None
                redirect_available = True

        return_values = [redirect_available, form]
        
        return_values.append(generic_formset) if generic_formset is not None else None
        
        # related forms block
        if self._first_related_model_form is not None or self._second_related_model_form is not None:
            return_values.extend(self._related_forms(
                method=method,
                post_dict=post_dict,
                files_dict=files_dict,
                instance=self._object
            ))
        
        # related formsets block
        if self._first_related_model_in_formset is not None:
            return_values.extend(self._related_inline_formsets(
                method=method,
                post_dict=post_dict,
                files_dict=files_dict,
                instance=self._object
            ))

        return return_values

    def _create_object(self, *, post_dict, files_dict=None, method):
        '''
        method for creating object in singleton model
        return values in next order -> 
            tuple(
                redirect_available: bool, 
                form: form object of self._form_class, 
                generic_formset:Optional[filled formset])
        '''

        redirect_available = False
        form = self._form_class()

        # generic formset block
        generic_formset = None
        if self._generic_model is not None:
            GenericFormset = generic_inlineformset_factory(self._generic_model, extra=self._generic_extra_forms, can_delete=True)
            generic_formset = GenericFormset(
                queryset=self._generic_model.objects.none(), prefix=self._generic_form_prefix)

        if method == 'POST':
            form = self._form_class(post_dict, files_dict)
            if form.is_valid():
                if generic_formset is None:
                    new_object = form.save()
                    redirect_available = True
                else:
                    new_object = form.save(commit=False)

                    # generic formset block
                    generic_formset = GenericFormset(post_dict, files_dict, instance=new_object, prefix=self._generic_form_prefix)
                    if generic_formset.is_valid():
                        new_object.save()
                        generic_formset.save()
                        redirect_available = True
        
        return_values = [redirect_available, form]
        return_values.append(generic_formset) if generic_formset is not None else None

        # related forms block
        if self._first_related_model_form is not None or self._second_related_model_form is not None:
            return_values.extend(self._related_forms(
                method=method,
                post_dict=post_dict,
                files_dict=files_dict,
                instance=new_object
            ))
        
        # related formsets block
        if self._first_related_model_in_formset is not None:
            return_values.extend(self._related_inline_formsets(
                method=method,
                post_dict=post_dict,
                files_dict=files_dict,
                instance=new_object
            ))

        return return_values

    def _related_inline_formsets(self, method: str, post_dict: dict, files_dict: dict, instance) -> tuple[inlineformset_factory]:
        FirstInlineFormSet = inlineformset_factory(self._model, 
            self._first_related_model_in_formset, extra=0,
            fields=self._first_related_model_in_formset_fields,
            can_delete=True)
        first_inlineformset = FirstInlineFormSet(instance=instance)  
        if method == 'POST':
            first_inlineformset = FirstInlineFormSet(post_dict, files_dict, instance=instance)
            if first_inlineformset.is_valid():
                first_inlineformset.save()

        return (first_inlineformset, ) 

    def _related_forms(self, method: str, post_dict: dict, files_dict: dict, instance):
        if method == 'POST':
            first_related_object = second_related_object = None
            if self._first_related_model_form is not None:
                first_related_model_form = self._first_related_model_form(post_dict, 
                    files_dict, prefix=self._first_related_model_form_prefix)
                if first_related_model_form.is_valid():
                    first_related_object = first_related_model_form.save(commit=False)
                    first_related_object.foreign_key = instance
                    first_related_object.save()
            if self._second_related_model_form is not None:
                second_related_model_form = self._second_related_model_form(post_dict, 
                    files_dict, prefix=self._second_related_model_form_prefix)
                if second_related_model_form.is_valid():
                    second_related_object = second_related_model_form.save(commit=False)
                    second_related_object.foreign_key = instance
                    second_related_object.save()
        else:
            if self._first_related_model_form is not None:
                first_related_model_form = self._first_related_model_form(prefix=self._first_related_model_form_prefix)
            if self._second_related_model_form is not None:
                second_related_model_form = self._second_related_model_form(prefix=self._second_related_model_form_prefix)
            
        return_values = []
        return_values.append(first_related_model_form) if self._first_related_model_form is not None else None
        return_values.append(second_related_model_form) if self._second_related_model_form is not None else None
        return return_values

    def as_view(self, values):
        pass