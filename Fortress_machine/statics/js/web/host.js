/**
 * Created by lenovo on 2017/5/7.
 */


$(document).ready(function () {
    bindShowHost();
    bindCheckAll();
    bindCancelAll();
    bindReverseAll();
    bindFileMode();
    bindExecuteCMD();
    $('#title_status').hide();
});
/*
 *  主机展示
 */
function bindShowHost() {
    $('.panel-body .list-group-item').click(function () {
        $(this).next().toggle(500);
    })
}
/*
 *  全选
 */
function bindCheckAll() {
    $('#idCheckAll').click(function () {
        $('.host-checkbox').addClass('active');
    })
}
/*
 *  取消
 */
function bindCancelAll() {
    $('#idCancelAll').click(function () {
        $('.host-checkbox').each(function () {
            if($(this).hasClass('active')){
                $(this).removeClass('active');
            }
        })
    })
}
/*
 *  反选
 */
function bindReverseAll() {
    $('#idReverseAll').click(function () {
        $('.host-checkbox').each(function () {
            if($(this).hasClass('active')){
                $(this).removeClass('active');
            }else {
                $(this).addClass('active');
            }
        })
    })
}
/*
 *  文件模式选择
 */
function bindFileMode() {
    $('#file_type').change(function () {
        var inputEle = $('#local_file_path');
        if($(this).val() === 'get'){
            inputEle.parent().addClass('hide');
        }else {
            inputEle.parent().removeClass('hide');
        }
    })
}
/*
 *  解析并执行相关命令
 */
function bindExecuteCMD() {
    $('#idExecute').click(function () {
        // 声明获取执行主机ID数组
        var selectedHostIds = [];
        // 声明Ajax提交数据的字典
        var postData = {};
        // 声明执行命令类型
        var executeType = $(this).attr('exeute-type');
        // 声明解除跨站请求伪造
        var csrfToken = $("input[name='csrfmiddlewaretoken']").val();
        // 声明提交的Url
        var requestUrl;
        $('.host-checkbox').each(function () {
            if($(this).hasClass('active')){
                var hostID = $(this).find(':checkbox').val();
                selectedHostIds.push(hostID)
            }
        });
        if(!selectedHostIds.length){
            alert("必须选择主机！");
            return false;
        }

        if(executeType === 'cmd'){
            // 获取命令
            var cmdText = $('#cmd_input').val().trim();
            if (!cmdText.length){
                alert("必须输入要执行的命令！");
                return false;
            }
            requestUrl = '/hosts-cmd.html';
            postData = {
                'selectedHostIds': selectedHostIds,
                'executeType': executeType,
                'cmdText': cmdText
            }
        }else if(executeType === 'file'){
            // 获取文件模式
            var file_type = $('#file_type').val();
            // 获取本地文件路径
            var local_file_path = $('#local_file_path').val().trim();
            // 获取远程文件路径
            var remote_file_path = $('#remote_file_path').val().trim();
            if(!file_type){
                alert('选择相应的文件上传模式...');
                return false;
            }else if(file_type === 'post'){
                if(!local_file_path){
                    alert('请填写上传文件的本地目标路径...');
                    return false;
                }
            }
            if(!remote_file_path){
                alert('请填写远程文件的目标路径');
                return false;
            }
            requestUrl = '/hosts-file.html';
            // 构建传送数据的字典
            postData = {
                'executeType': executeType,
                'file_type': file_type,
                'local_file_path': local_file_path,
                'remote_file_path': remote_file_path,
                'selectedHostIds': selectedHostIds
            }
        }else {
            console.log('其它')
        }

        // 远程执行未返回结果禁止重复发起请求
        $(this).addClass('disabled');
        $('#task_result_container').empty();

        $.ajax({
            url: requestUrl,
            type: 'post',
            data: {
                'csrfmiddlewaretoken': csrfToken,
                'postData': JSON.stringify(postData)
            },
            success: function (response) {
                if(response.status){
                    // 初始化服务器结果信息
                    initializeData(response, requestUrl)
                }
            },
            traditional: true
        })
    })
}
/*
 *  初始化单元格面板
 */
function initializeData(response, requestUrl) {
    $('#title_status').text(response.message).show('2000');
    $.each(response.data.hosts_info, function (index, hostInfo) {
        var li = document.createElement('li');
        var span = document.createElement('span');
        var pre = document.createElement('pre');
        $(li).attr({'log-id': hostInfo.id});
        $(li).css({'list-style': 'none', 'margin-bottom': '5px'});
        $(li).html(
            '状态：<span class="label label-mint">Info</span> ' +
            ' 主机名称：' + hostInfo.host_to_remote_user__host__name +
            ' 远程地址：' + hostInfo.host_to_remote_user__host__ip_addr +
            ' 远程登陆用户：' + hostInfo.host_to_remote_user__remote_user__username
        );
        $(span).attr({'log_status': 'true'});
        $(li).append(span);
        $(pre).text('等待结果传输中...');
        $('#task_result_container').append(li, pre);
    });

    refreshData = setInterval(function () {
        refreshTaskResult(response.data.task_id)
    }, 2000)
}
/*
 *  持续获取远程结果
 */
function refreshTaskResult(task_id, requestUrl) {
    var csrfToken = $("input[name='csrfmiddlewaretoken']").val();
    $.ajax({
        url: requestUrl,
        type: 'put',
        data: {
            'csrfmiddlewaretoken': csrfToken,
            'task_id': task_id
        },
        success: function (response) {
            var status = true;
            if(response.status){
                $.each(response.data.putData, function (index, taskLogInfo) {
                    var li = $('li[log-id='+ taskLogInfo.id +']');
                    var statusSpan = li.children().first();
                    if(taskLogInfo.status===0){
                        status = false;
                    }else if(taskLogInfo.status===1){
                        statusSpan.removeClass('label-mint').addClass('label-success').text('Success');
                    }else{
                        statusSpan.removeClass('label-mint').addClass('label-danger').text('Danger');
                    }
                    li.next().text(taskLogInfo.result)
                })
            }
            if(status){
                clearInterval(refreshData);
                // 解除命令
                $('#idExecute').removeClass('disabled');
                $('#title_status').removeClass().addClass('btn btn-success').text('当前所有主机获取成功')
                setTimeout(function () {
                    $('#title_status').hide(1000).empty();
                }, 3000)
            }
        }
    })
}