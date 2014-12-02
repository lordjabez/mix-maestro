(function() {


  'use strict';


  angular.module('mixMaestroApp').controller('MixCtrl', ['$scope', '$stateParams', '$http', '$timeout', '$ionicLoading', function($scope, $stateParams, $http, $timeout, $ionicLoading) {


    $ionicLoading.show();


    var pollTimeout;


    var getMix = function() {
      cancelMixPoll();
      $http.get('/auxes/' + $stateParams.id + '/inputs')
        .success(function(data) {
          $scope.name = data.name;
          $scope.inputs = [];
          angular.forEach(data.inputs, function(value, key) {
            value.id = key;
            $scope.inputs.push(value);
          });
          $ionicLoading.hide();
        })
        .error(function() {
          delete $scope.name;
          delete $scope.inputs;
          $ionicLoading.show();
        })
        .finally(function() {
          scheduleMixPoll(5 * 1000);
        });
    }


    var scheduleMixPoll = function(delay) {
      pollTimeout = $timeout(getMix, delay);
    };


    var cancelMixPoll = function() {
      $timeout.cancel(pollTimeout);
    }


    $scope.$on('$destroy', cancelMixPoll);


    getMix();


    $scope.setLevel = function(id, level) {
      $http.put('/auxes/' + $stateParams.id + '/inputs/' + id, {'level': level})
        .success(function() {
          scheduleMixPoll(0.5 * 1000);
        });
    };


  }]);


}());