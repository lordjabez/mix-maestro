(function() {


  'use strict';


  angular.module('mixMaestroApp').controller('MixesCtrl', ['$scope', '$http', '$timeout', function($scope, $http, $timeout) {


    var pollTimeout;


    var getAuxes = function() {
      $http.get('/auxes')
        .success(function(data) {
          $scope.auxes = data;
        })
        .error(function() {
          delete $scope.auxes;
        })
        .finally(function() {
          scheduleAuxesPoll(10 * 1000);
        });
    }


    var scheduleAuxesPoll = function(delay) {
      pollTimeout = $timeout(getAuxes, delay);
    };


    $scope.$on('$destroy', function() {
      $timeout.cancel(pollTimeout);
    });


    getAuxes();


  }]);


}());