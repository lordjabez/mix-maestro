(function() {


  'use strict';


  angular.module('mixMaestroApp').controller('MixCtrl', ['$scope', '$stateParams', '$http', '$timeout', function($scope, $stateParams, $http, $timeout) {


    var pollTimeout;


    var getMix = function() {
      $http.get('/auxes/' + $stateParams.id + '/inputs')
        .success(function(data) {
          $scope.name = data.name;
          $scope.inputs = data.inputs;
        })
        .error(function() {
          delete $scope.name;
          delete $scope.inputs;
        })
        .finally(function() {
          scheduleMixPoll(1 * 1000);
        });
    }


    var scheduleMixPoll = function(delay) {
      pollTimeout = $timeout(getMix, delay);
    };


    $scope.$on('$destroy', function() {
      $timeout.cancel(pollTimeout);
    });


    getMix();


    $scope.setLevel = function(id, level) {
      $http.put('/auxes/' + $stateParams.id + '/inputs/' + id, {'level': level})
        .success(function() {
          // TODO
        })
        .error(function() {
          // TODO
        });
    };


  }]);


}());