(function() {


  'use strict';


  angular.module('mixMaestroApp', ['ionic'])


    .run(function($ionicPlatform) {

      $ionicPlatform.ready(function() {

        if(window.cordova && window.cordova.plugins.Keyboard) {
          cordova.plugins.Keyboard.hideKeyboardAccessoryBar(true);
        }

        if(window.StatusBar) {
          StatusBar.styleDefault();
        }

      });

    })


    .config(function($stateProvider, $urlRouterProvider) {

      $stateProvider

        .state('app', {
          url: "/app",
          abstract: true,
          templateUrl: "templates/mixes.html",
          controller: 'MixesCtrl'
        })

        .state('app.mixes', {
          url: "/mixes",
          views: {
            'menuContent' :{
              templateUrl: "templates/mix.html"
            }
          }
        })

        .state('app.mix', {
          url: "/mixes/{id}",
          views: {
            'menuContent' :{
              templateUrl: "templates/mix.html",
              controller: 'MixCtrl'
            }
          }
        });

      $urlRouterProvider.otherwise('/app/mixes');

  });


}());