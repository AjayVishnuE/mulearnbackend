import uuid

from rest_framework.views import APIView

from db.task import InterestGroup
from utils.permission import CustomizePermission
from utils.permission import JWTUtils, RoleRequired
from utils.response import CustomResponse
from utils.types import RoleType, WebHookActions, WebHookCategory
from utils.utils import CommonUtils, DateTimeUtils, DiscordWebhooks
from .dash_ig_serializer import InterestGroupSerializer


class InterestGroupAPI(APIView):
    authentication_classes = [CustomizePermission]  # for logged in users

    # GET Request to show all interest groups. Params availiable:[sortBy, search, perPage, pageIndex]
    @RoleRequired(roles=[RoleType.ADMIN, ])  # for admin
    def get(self, request):
        ig_serializer = InterestGroup.objects.all()
        paginated_queryset = CommonUtils.get_paginated_queryset(ig_serializer, request,
                                                                ['name', 'id', 'updated_by', 'created_by', 'updated_at',
                                                                 'created_at', 'count']
                                                                )
        ig_serializer_data = InterestGroupSerializer(paginated_queryset.get('queryset'), many=True).data

        return CustomResponse().paginated_response(data=ig_serializer_data,
                                                   pagination=paginated_queryset.get('pagination'))

    # POST Request to create a new interest group
    # body should contain 'name': '<new name of interest group>'
    @RoleRequired(roles=[RoleType.ADMIN, ])
    def post(self, request):
        user_id = JWTUtils.fetch_user_id(request)
        ig_data = InterestGroup.objects.create(
            id=uuid.uuid4(),
            name=request.data.get('name'),
            updated_by_id=user_id,
            updated_at=DateTimeUtils.get_current_utc_time(),
            created_by_id=user_id,
            created_at=DateTimeUtils.get_current_utc_time())
        serializer = InterestGroupSerializer(ig_data)
        DiscordWebhooks.channelsAndCategory(
            WebHookCategory.INTEREST_GROUP.value,
            WebHookActions.CREATE.value,
            request.data.get('name')
        )
        return CustomResponse(response={"interestGroup": serializer.data}).get_success_response()

    # PUT Request to edit an InterestGroup. Use endpoint + /<id>/
    # body should contain 'name': '<new name of interst group>' for edit
    @RoleRequired(roles=[RoleType.ADMIN, ])
    def put(self, request, pk):
        user_id = JWTUtils.fetch_user_id(request)
        igData = InterestGroup.objects.get(id=pk)
        oldName = igData.name
        igData.name = request.data.get('name')
        igData.updated_by_id = user_id
        igData.updated_at = DateTimeUtils.get_current_utc_time()
        igData.save()
        serializer = InterestGroupSerializer(igData)
        DiscordWebhooks.channelsAndCategory(
            WebHookCategory.INTEREST_GROUP.value,
            WebHookActions.EDIT.value,
            igData.name,
            oldName
        )
        return CustomResponse(
            response={"interestGroup": serializer.data}
        ).get_success_response()

    # DELETE Request to delete an InterestGroup. Use endpoint + /<id>/
    @RoleRequired(roles=[RoleType.ADMIN, ])
    def delete(self, request, pk):
        igData = InterestGroup.objects.get(id=pk)
        igData.delete()
        serializer = InterestGroupSerializer(igData)
        DiscordWebhooks.channelsAndCategory(
            WebHookCategory.INTEREST_GROUP.value,
            WebHookActions.DELETE.value,
            igData.name
        )
        return CustomResponse(
            response={"interestGroup": serializer.data}
        ).get_success_response()


class InterestGroupCSV(APIView):
    authentication_classes = [CustomizePermission]

    @RoleRequired(roles=[RoleType.ADMIN, ])
    def get(self, request):
        ig_serializer = InterestGroup.objects.all()
        ig_serializer_data = InterestGroupSerializer(ig_serializer, many=True).data

        return CommonUtils.generate_csv(ig_serializer_data, 'Interest Group')



class InterestGroupGetAPI(APIView):
    authentication_classes = [CustomizePermission] 
    
    @RoleRequired(roles=[RoleType.ADMIN, ])
    def get(self, request, pk):
        igData = InterestGroup.objects.get(id=pk)
        serializer = InterestGroupSerializer(igData)
        return CustomResponse(response={"interestGroup": serializer.data}).get_success_response()
