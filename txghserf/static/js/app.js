/*
Simple JS Application to manage GitHub Hooks.
*/

var app = angular.module('githubhooks', ['ui.bootstrap']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.
      when('/login', {
        templateUrl: 'static/partials/login.html',
        controller: LoginCtrl
        }).
      when('/organizations', {
        templateUrl: 'static/partials/organizations.html',
        controller: OrganizationsCtrl
        }).
      when('/organization/:organization', {
        templateUrl: 'static/partials/organization.html',
        controller: OrganizationCtrl
        }).
      when('/organization/:organization/:repository', {
        templateUrl: 'static/partials/repository.html',
        controller: RepositoryCtrl
        }).
      otherwise({
        redirectTo: '/login'
    })
  }]).
  controller('rootCtrl', RootCtrl).
  factory('github', GitHubService)


function GitHubService($http, $location){
  var exports = {}
  var API_URL = 'https://api.github.com';

  var parseRelativeLinks = function(raw_links){
    var result= {}
    var members = raw_links.split(',')
    angular.forEach(
      members,
      function(value, key){
        var match = value.match('"*<(.*)>; rel="(\\w+)"')
        if (match) {
          result[match[2]] = match[1]
        }

      })
    return result
  }

  exports.GitHub = function(config){
      this.username = config.username
      this.password = config.password

      this.headers = {
        'Accept': 'application/vnd.github.raw',
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + Base64.encode(
          this.username + ':' + this.password)
      }

      this.getUser = function() {
        return $http({
          method: 'GET',
          url: API_URL + '/user',
          cache: true,
          headers: this.headers
          })
      }

      this.get = function(url) {
        var self = this
        return $http({
          method: 'GET',
          url: url,
          cache: true,
          params: {per_page: 1000},
          headers: self.headers
          })
      }

      this.post = function(url, data) {
        return $http({
          method: 'POST',
          data: data,
          url: url,
          headers: this.headers
          })
      }

      this.del = function(url) {
        return $http({
          method: 'DELETE',
          url: url,
          headers: this.headers
          })
      }

      this.patch = function(url, data) {
        return $http({
          method: 'PATCH',
          url: url,
          data: data,
          headers: this.headers
          })
      }

      return this
    }

  return exports
}

function RootCtrl($scope, $location) {

  $scope.github = ''
  $scope.account = ''
  $scope.alert = {}
  $scope.alert.info = ''
  $scope.alert.error = ''

  $scope.base_url = (
    $location.protocol() + '://' +
    $location.host() + ':' + $location.port() + '/' +
    'hook/'
    )

  $scope.getGitHub = function() {
    if (!$scope.github || !$scope.account) {
      $location.path('/')
      return
    }
    return $scope.github
  }

  $scope.goToLogin = function() {
    $location.path('/')
  }

  $scope.goToOrganizations = function() {
    $location.path('/organizations')
  }

  $scope.goToOrganization = function(organization) {
    $location.path('/organization/' + organization.login)
  }

  $scope.getOrganization = function(name) {
    var orgs = $scope.account.organizations
    var length = orgs.length
    for (var i = 0; i < length; i++) {
      if (orgs[i].login == name) {
        return orgs[i]
      }
    }
  }

  $scope.goToRepository = function(organization, repository) {
    $location.path(
      '/organization/' + organization.login + '/' + repository.name)
  }

  $scope.getRepository = function(organization, repository_name) {
    var repos = organization.repositories
    var length = repos.length
    for (var i = 0; i < length; i++) {
      if (repos[i].name == repository_name) {
        return repos[i]
      }
    }
  }

}

/*
Login handler.
*/
function LoginCtrl($scope, $rootScope, github) {

  $scope.user = {}
  $scope.user.name = ''
  $scope.user.password = ''

  $scope.doLogin = function() {
    $scope.$parent.alert.info = 'Authentication in progress...'


    hub = new github.GitHub({
      username: $scope.user.name,
      password: $scope.user.password
    })
    $scope.$parent.github = hub

    hub.getUser().
      success(function(data, status) {
        $scope.$parent.alert.info = ''
        $scope.$parent.alert.error = ''
        $scope.$parent.account = data
        $scope.$parent.goToOrganizations()
      }).
      error(function(data, status) {
        $scope.$parent.alert.info = ''
        $scope.$parent.alert.error = data.message
        $scope.$parent.goToLogin()
      })
  }
}

/*
Organizations for an account.
*/
function OrganizationsCtrl($scope) {

  var hub = $scope.$parent.getGitHub()
  if (!hub) return

  hub.get($scope.$parent.account.organizations_url).
    success(function(data, status, headers){
      $scope.$parent.account.organizations = data
    }).
    error(function(data, status){
      $scope.$parent.error = data.message
      $scope.$parent.goToLogin()
    })

}


/*
Repos for an organization.
*/
function OrganizationCtrl($scope, $routeParams) {

  var hub = $scope.$parent.getGitHub()
  if (!hub) return

  $scope.name = $routeParams.organization
  $scope.organization = $scope.$parent.getOrganization($scope.name)

  hub.get($scope.organization.repos_url).
    success(function(data, status){
      $scope.organization.repositories = data
    }).
    error(function(data, status){
      $scope.$parent.error = data.message
      $scope.$parent.goToLogin()
    })
}


/*
Hooks for a repository.
*/
function RepositoryCtrl($scope, $routeParams, $dialog) {

  $scope.alerts = []

  $scope.addError = function(message) {
    $scope.alerts.push({type: 'error', msg: message})
  }

  $scope.addInfo = function(message) {
    $scope.alerts.push({type: 'info', msg: message})
  }

  $scope.addSuccess = function(message) {
    $scope.alerts.push({type: 'success', msg: message})
  }

  $scope.closeAlert = function(index) {
    $scope.alerts.splice(index, 1)
  }

  $scope.clearAlert = function(index) {
    $scope.alerts.length = 0
  }

  $scope.canEdit = function(hook) {
    if (hook.name === 'web') {
      return true
    } else {
      return false
    }
  }

  $scope.getStatus = function(hook) {
    var result
    if (hook.active) {
      result = 'active'
    } else {
      result = 'disabled'
    }
    return result
  }

  /*
  Return the name of the hook.
  */
  $scope.getName = function(hook) {
    if (hook.name === 'web') {
      return hook.config.url
    } else {
      return hook.name
    }
  }

  /*
  Simple view of hook configuration.
  */
  $scope.onView = function(hook){
    var buttons = [
      {result:'ok', label: 'OK', cssClass: 'btn-primary'}]

    $dialog.messageBox(
      'Details for ' + hook.name,
      hook.config,
      buttons
      ).open()
  }

  /*
  Action pefromed when add hook is requested from GUI.
  */
  $scope.onAdd = function(){

    var options = {
      backdrop: true,
      keyboard: true,
      backdropClick: false,
      resolve: {
        base_url: $scope.$parent.base_url,
        hook: undefined
      },
      templateUrl:  '/static/partials/hook.html',
      controller: 'HookCtrl'
    };

    $dialog.dialog(options).open().then(function(new_hook){
      if (new_hook) {
        $scope._addHook(new_hook)
      }
    })
  }

  $scope._addHook = function(new_hook){
    $scope.addInfo('Adding new hook...')
    hub.post($scope.repository.hooks_url, new_hook).
      success(function(data, status){
        $scope.clearAlert()
        $scope.addSuccess('New Hook added.')
        $scope.repository.hooks.push(data)
      }).
      error(function(data, status){
        $scope.clearAlert()
        $scope.addError(data)
      })
  }

  /*
  Action pefromed when edit hook is requested from GUI.
  */
  $scope.onEdit = function(hook){

    var options = {
      backdrop: true,
      keyboard: true,
      backdropClick: false,
      resolve: {
        base_url: $scope.$parent.base_url,
        hook: angular.copy(hook)
        },
      templateUrl:  '/static/partials/hook.html',
      controller: 'HookCtrl'
    };

    $dialog.dialog(options).open().then(function(result){
      if(result) {
        $scope._editHook(hook, result)
      }
    })
  }

  /*
  Perform hook editing.
  */
  $scope._editHook = function(hook, update) {
    $scope.addInfo('Updating hook ' + hook.id)
    hub.patch(hook.url, update).
      success(function(data, status){
        $scope.clearAlert()
        $scope.addSuccess('Hook updated')
        angular.extend(hook, data)
      }).
      error(function(data, status){
        $scope.clearAlert()
        $scope.addError(data)
      })
  }

  /*
  Action performed when delete button was pressed.
  */
  $scope.onDelete = function(hook){
    var title = 'Delete hook - ' + hook.name
    var msg = 'All hook inforamation will be lost.'
    var buttons = [
      {result:'cancel', label: 'Cancel'},
      {result:'delete', label: 'OK', cssClass: 'btn-danger'}]

    $dialog.messageBox(title, msg, buttons)
      .open()
      .then(function(result){
        if (result !== 'delete') {
          return
        }
        $scope._deleteHook(hook)
    })
  }

  /*
  Delete a hook.
  */
  $scope._deleteHook = function(hook){
    $scope.addInfo('Removing hook ' + hook.id)
    hub.del(hook.url).
      success(function(data, status){
        angular.forEach(
          $scope.repository.hooks,
          function(value, key){
            if (hook.id === value.id) {
              $scope.repository.hooks.splice(key, 1)
              return
            }
          })
        $scope.clearAlert()
        $scope.addSuccess('Hook removed.')
      }).
      error(function(data, status){
        $scope.clearAlert()
        $scope.addError(data)
      })
  }

  $scope.onTest = function(hook){
    var title = 'Test for ' + hook.name
    var buttons = [
      {result:'ok', label: 'OK', cssClass: 'btn-primary'}]

    hub.post(hook.test_url).
      success(function(data, status){
        $dialog.messageBox(
          title,
          'Test sent',
          buttons
          ).open()
      }).
      error(function(data, status){
        $dialog.messageBox(
          title,
          'Failed: ' + status + '-' + data,
          buttons
          ).open()
      })
  }

  var hub = $scope.$parent.getGitHub()
  if (!hub) return

  $scope.organization = $scope.$parent.getOrganization(
    $routeParams.organization)
  $scope.repository = $scope.$parent.getRepository(
    $scope.organization, $routeParams.repository)

  hub.get($scope.repository.hooks_url).
    success(function(data, status){
      $scope.repository.hooks = data
    }).
    error(function(data, status){
      $scope.$parent.error = data.message
      $scope.$parent.goToLogin()
    })

}


/*
Controller required for Hook add dialog.
*/
function HookCtrl($scope, dialog, base_url, hook){

  $scope.hook = {}
  $scope.hook.config = {}
  $scope.hook.config.content_type = 'form'

  $scope.base_url = base_url
  $insecure = true

  if (hook) {
    angular.extend($scope.hook, hook)
    $scope.title = "Edit hook " + hook.id
    $scope.action_name = "Save"
    if ($scope.hook.config.insecure_ssl == '1') {
      $scope.hook.config.insecure_ssl = true
    } else {
      $scope.hook.config.insecure_ssl = false
    }
  } else {
    $scope.title = "Add new hook"
    $scope.hook.name = 'web'
    $scope.hook.active = true
    $scope.hook.config.url = base_url
    $scope.action_name = "Add new hook"
  }

  $scope.close = function(result){
    dialog.close(result);
  }

  $scope.doSubmit = function() {
    if (!angular.isArray($scope.hook.events)){
      $scope.hook.events = $scope.hook.events.split(',')
      angular.forEach(
        $scope.hook.events,
        function(value, key) {
          $scope.hook.events[key] = $scope.hook.events[key].replace(/^\s+|\s+$/g, '')
        })
    }

    if ($scope.hook.config.insecure_ssl) {
      $scope.hook.config.insecure_ssl = '1'
    } else {
      $scope.hook.config.insecure_ssl = '0'
    }

    dialog.close($scope.hook);
  }
}
